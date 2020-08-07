import discord
import logging
from pathlib import Path
from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from discord.ext import commands, tasks
import pyrfc3339 as rfc3339
from .google_calendar import GoogleCalendar
from datafile import Data,DataFile
import dateutil.parser
import dateutil.tz
from dateutil.tz import tzutc
from datetime import time, datetime, timedelta

log = logging.getLogger('CalendarCog')

@dataclass
class Subscription(Data):
    calendar_id: str
    user_id: int
    channel_id: int
    guild_id: int

@dataclass
class User(Data):
    user_id: int
    refresh_token: str = None

@dataclass(order=True)
class Event(Data):
    start: datetime
    title: str
    description: str
    subscription: Subscription
    end: datetime = None

@dataclass
class CalendarData(DataFile):
    summary_day: Optional[int] = None
    summary_hour: Optional[int] = None
    users: Dict[int, User] = field(default_factory=dict)
    subscriptions: List[Subscription] = field(default_factory=list)

class CalendarQueue(PriorityQueue):
    def _put(self, item):
        if item not in self.queue:
            return super()._put(item)

class Calendar(commands.Cog):
    """ Calendar commands """

    def __init__(self, bot):
        self.bot = bot
        self.events = CalendarQueue()
        self.awaiting_user_auth = {}
        path = str(Path(self.bot.data_path, 'calendar.yml'))
        self.data = CalendarData().from_yaml(path=path)
        self.collect_next_events()
        self.set_next_execution()

    @commands.Cog.listener()
    async def on_ready(self):
        self.tick.start()

    def set_next_execution(self):
        #execute once an hour, or sooner if we have an event coming up
        next_execution = datetime.utcnow().replace(tzinfo=tzutc(),minute=0,second=0)+timedelta(hours=1)
        if not self.events.empty():
            peek = self.events.queue[0]
            next_execution = min(next_execution, peek.start)
            self.next_execution = next_execution
            log.debug("Next Calendar Update: {}, Next Event: {}".format(rfc3339.generate(next_execution),
            rfc3339.generate(peek.start)))

    @tasks.loop()
    async def tick(self):
        #block until it's time to chime
        await discord.utils.sleep_until(self.next_execution)
        await self.chime()
        self.collect_next_events()
        self.set_next_execution()

    async def chime(self):
        now = datetime.utcnow().replace(tzinfo=tzutc())
        summary_chime = False
        if self.data.summary_day and self.data.summary_hour:
            if now.weekday is self.data.summary_day and now.hour is self.data.summary_hour:
                summary_chime = True
        while not self.events.empty():
            peek = self.events.queue[0]
            if now >= peek.start:
                event = self.events.get()
                message = "{}".format(event.title)
                if event.description:
                    message = "{}\n>>> {}".format(message, event.description)
                out_chan = discord.utils.get(self.bot.get_all_channels(),
                        id=event.subscription.channel_id)
                await out_chan.send(message)
            else:
                # the event starts after now, PQ is in order, and this isn't a summary
                break
        if summary_chime and not self.events.empty():
            temp = []
            message = "**Events This Week**"
            while not self.events.empty():
                event = self.events.get()
                temp.append(event)
                message = message + "\n- {} on {}".format(event.title, event.start.strftime('%a at %H:%M'))
            for event in temp:
                self.events.put(event)
            out_chan = discord.utils.get(self.bot.get_all_channels(),
                    id=event.subscription.channel_id)
            await out_chan.send(message)

    def collect_next_events(self):
        seen = []
        while not self.events.empty():
            self.events.get()
        for subscription in self.data.subscriptions:
            if subscription.calendar_id not in seen:
                seen.append(subscription.calendar_id)
                calendar_user = self.data.users.get(subscription.user_id)
                calendar = GoogleCalendar(calendar_id=subscription.calendar_id,
                        refresh_token=calendar_user.refresh_token)
                time_min = rfc3339.generate(datetime.utcnow().replace(tzinfo=tzutc()))
                time_max = rfc3339.generate(
                        (datetime.utcnow() + timedelta(days=7)).replace(tzinfo=tzutc())
                        )
                calendar_items = calendar.list_events(orderBy="startTime", timeMin=time_min,
                        timeMax=time_max,singleEvents=True)["items"]
                for item in calendar_items:
                    start_time = None
                    if "dateTime" in item["start"]:
                        start_time = rfc3339.parse(item["start"]["dateTime"])
                    else:
                        start_time = datetime.strptime(item["start"]["date"], '%Y-%m-%d').replace(hour=0,minute=0,second=0,tzinfo=tzutc())
                    if datetime.utcnow().replace(tzinfo=tzutc()) >= start_time:
                        continue
                    end_time = None
                    if item["end"]:
                        if "dateTime" in item["end"]:
                            end_time = rfc3339.parse(item["end"]["dateTime"])
                    title = item["summary"]
                    description = item.get("description")
                    event = Event(start=start_time, end=end_time, title=title,
                            description=description, subscription=subscription)
                    self.events.put(event)

    @commands.command()
    async def summary(self, ctx, summary_day : int, summary_hour : int):
        channel = ctx.message.channel
        errors = []
        if not 0 <= summary_day <= 6:
            errors.append("summary day out of range")
        if not 0 <= summary_hour <= 23:
            errors.append("summary hour out of range")
        if errors:
            await ctx.channel.send(", ".join(errors))
            return
        self.data.summary_day = summary_day
        self.data.summary_hour = summary_hour
        self.data.save()
        await ctx.channel.send("summary set")

    @commands.command()
    async def subscribe(self, ctx, calendar_id : str, sub_chan : discord.TextChannel):
        channel = ctx.message.channel
        user = ctx.message.author
        if not sub_chan:
            await channel.send("Could not find channel {}".format(chan))
            return
        if user.id not in self.data.users:
            calendar = GoogleCalendar()
            url = calendar.get_auth_url()
            self.awaiting_user_auth[user.id] = calendar
            message = "Click the following link to authorize me to view your Google Calendars." \
                    "Once Done, use the auth_token command to submit the code it displays." \
                    "{}".format(url)
            await channel.send(message)
        else:
            refresh_token = self.data.users.get(user.id).refresh_token
            calendar = GoogleCalendar(calendar_id=calendar_id, refresh_token=refresh_token)
            info = calendar.get_info()
            subscription = Subscription(calendar_id=info["id"], user_id=user.id,
                    channel_id=sub_chan.id, guild_id=channel.guild.id)
            if subscription in self.data.subscriptions:
                await channel.send("Already subscribed!")
                return
            self.data.subscriptions.append(subscription)
            self.data.save()
            await channel.send("Subscribed {} to {}".format(sub_chan, info['summary']))

    @commands.command()
    async def auth_token(self, ctx, *, auth_token : str):
        channel = ctx.message.channel
        user = ctx.message.author
        awaiting_auth = self.awaiting_user_auth.get(user.id)
        if not awaiting_auth:
            await channel.send("I don't have any auths open, maybe restart the subscription?")
            return
        refresh_token = awaiting_auth.submit_auth_code(auth_token)
        if user.id not in self.data.users:
            user_data = User(user_id=user.id, refresh_token=refresh_token)
            self.data.users[user.id] = user_data
            self.data.save()
        await channel.send('authed')

