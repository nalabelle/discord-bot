"""
Cog for Calendar Command
"""

import logging
from pathlib import Path
from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from datafile import Data,DataFile
from dateutil import tz
from dateutil.tz import tzutc
import discord
from discord.ext import commands, tasks
import pyrfc3339 as rfc3339
from .google_calendar import GoogleCalendar
log = logging.getLogger('CalendarCog')

@dataclass
class Subscription(Data):
    """Subscription Storage Dataclass"""
    calendar_id: str
    user_id: int
    channel_id: int
    guild_id: int

@dataclass
class User(Data):
    """User Storage Dataclass"""
    user_id: int
    refresh_token: str = None

@dataclass(order=True)
class Event(Data):
    """Event Storage Dataclass"""
    start: datetime
    calendar_tz: str
    title: str
    description: str
    subscription: Subscription
    end: datetime = None

@dataclass
class CalendarData(DataFile):
    """Calendar Data Storage"""
    summary_day: Optional[int] = None
    summary_hour: Optional[int] = None
    users: Dict[int, User] = field(default_factory=dict)
    subscriptions: List[Subscription] = field(default_factory=list)

class CalendarQueue(PriorityQueue):
    """Priority Queue for holding calendar events in chronological order"""

    def _put(self, item):
        if item not in self.queue:
            return super()._put(item)
        return None

class Calendar(commands.Cog):
    """ Calendar commands """

    def __init__(self, bot):
        self.bot = bot
        self.next_execution = None
        self.events = CalendarQueue()
        self.awaiting_user_auth = {}
        path = str(Path(self.bot.data_path, 'calendar.yml'))
        self.data = CalendarData().from_yaml(path=path)
        self.collect_next_events()
        self.set_next_execution()
        # pylint: disable=no-member
        self.tick.start()

    def set_next_execution(self):
        #execute once an hour, or sooner if we have an event coming up
        next_execution = datetime.utcnow().replace(tzinfo=tzutc(),minute=0,second=0) \
            + timedelta(hours=1)
        if not self.events.empty():
            peek = self.events.queue[0]
            next_execution = min(next_execution, peek.start)
            log.debug("Next Event: %s", rfc3339.generate(peek.start))
        self.next_execution = next_execution
        log.debug("Next Calendar Update: %s", rfc3339.generate(next_execution))

    @tasks.loop()
    async def tick(self):
        log.debug("Tick start")
        if self.next_execution is not None:
            #block until it's time to chime
            log.debug("Waiting until %s", rfc3339.generate(self.next_execution))
            await discord.utils.sleep_until(self.next_execution)
        await self.chime()
        self.collect_next_events()
        self.set_next_execution()
        log.debug("Tick end")

    @tick.before_loop
    async def before_tick(self):
        log.debug("Waiting for bot ready to start tick loop")
        await self.bot.wait_until_ready()
        log.debug("Starting tick loop")

    def dtf(self, d_t : datetime) -> str:
        return d_t.strftime('%a, %H:%M')

    def event_to_embed(self, event) -> discord.Embed:
        event_tz = tz.gettz(event.calendar_tz)
        formatted_start = self.dtf(event.start.astimezone(event_tz))
        formatted_end = self.dtf(event.end.astimezone(event_tz))
        return discord.Embed.from_dict({
            "title": event.title,
            "description": event.description,
            "timestamp": event.start.timestamp(),
            "fields": [
                {
                    "name": 'Start',
                    "value": formatted_start,
                    "inline": True
                },
                {
                    "name": 'End',
                    "value": formatted_end,
                    "inline": True
                },
            ]
        })

    async def chime(self):
        now = datetime.utcnow().replace(tzinfo=tzutc())
        while not self.events.empty():
            peek = self.events.queue[0]
            if now >= peek.start:
                event = self.events.get()
                out_chan = discord.utils.get(self.bot.get_all_channels(),
                        id=event.subscription.channel_id)
                await out_chan.send(embed=self.event_to_embed(event))
            else:
                # the event starts after now, PQ is in order, and this isn't a summary
                break
        if self.data.summary_day and self.data.summary_hour:
            if now.weekday is self.data.summary_day and now.hour is self.data.summary_hour:
                await self.send_summary_output()

    async def send_summary_output(self, channel_id : Optional[str] = None) -> None:
        for embed_channel_id, embed in self.summary_embeds(channel_id).items():
            log.debug("Sending %d summary events to %s", len(embed.fields), embed_channel_id)
            out_chan = discord.utils.get(self.bot.get_all_channels(), id=embed_channel_id)
            await out_chan.send(embed=embed)

    def summary_embeds(self, channel_id : Optional[str] = None) -> Dict[str, discord.Embed]:
        embeds = dict()
        embed = discord.Embed(title="**Events This Week**")
        log.debug("Getting summary embeds")
        for event in self.events.queue:
            log.debug("Summary event found for channel %s", event.subscription.channel_id)
            if channel_id and channel_id != event.subscription.channel_id:
                log.debug("Skipping event for other channel")
                continue
            event_tz = tz.gettz(event.calendar_tz)
            period = "{} to {}".format(self.dtf(event.start.astimezone(event_tz)),
                self.dtf(event.end.astimezone(event_tz)))
            embed = embeds.setdefault(event.subscription.channel_id, embed.copy())
            embed.add_field(name=event.title,value=period, inline=True)
        return embeds

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
                    calendar_tz = item["start"].get("timeZone", calendar.get_info()["timeZone"])
                    if "dateTime" in item["start"]:
                        start_time = rfc3339.parse(item["start"]["dateTime"])
                    else:
                        start_time = datetime.strptime(item["start"]["date"], '%Y-%m-%d') \
                            .replace(hour=0,minute=0,second=0,tzinfo=tzutc())
                    if datetime.utcnow().replace(tzinfo=tzutc()) >= start_time:
                        continue
                    end_time = None
                    if item["end"]:
                        if "dateTime" in item["end"]:
                            end_time = rfc3339.parse(item["end"]["dateTime"])
                    title = item["summary"]
                    description = item.get("description")
                    event = Event(start=start_time, end=end_time, title=title,
                            description=description, subscription=subscription,
                            calendar_tz=calendar_tz)
                    self.events.put(event)

    @commands.group()
    async def cal(self, ctx):
        """
        Calendar Commands
        """

    @cal.command()
    @commands.is_owner()
    async def debug(self, ctx):
        """
        Outputs debug information
        """
        next_execution = "None scheduled"
        if self.next_execution:
            next_execution = rfc3339.generate(self.next_execution)
        now = datetime.utcnow().replace(tzinfo=tzutc())
        now = "{}, DOW {}, HR {}".format(rfc3339.generate(now), now.weekday, now.hour)
        summary = "No summary"
        if self.data.summary_day:
            summary = "DOW {}, HR {}".format(self.data.summary_day, self.data.summary_hour)
        subscriptions = self.data.subscriptions
        if not subscriptions:
            subscriptions = ["No subscriptions"]
        message = ("```"
            "Now: {}\n"
            "Next Execution: {}\n"
            "Summary: {}\n"
            "Events in queue: {}\n"
            "Subscriptions:\n"
            "  {}\n"
            "```").format(
            now,
            next_execution,
            summary,
            self.events.qsize(),
            "\n".join(["  {}".format(x) for x in subscriptions])
            )
        await ctx.channel.send(message)

    @cal.command()
    async def summary(self, ctx):
        """
        Outputs upcoming events
        """
        await self.send_summary_output(ctx.channel.id)

    @cal.command()
    @commands.is_owner()
    async def set_summary(self, ctx, summary_day : int, summary_hour : int):
        """
        Sets the date and time for the bot to put a summary in the the channel
        arguments:
          Day of the week (0-6)
          Hour of the day (0-23)
        """
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

    @cal.command()
    async def subscribe(self, ctx, calendar_id : str, sub_chan : discord.TextChannel):
        """
        Subscribes a Google Calendar to a Discord Channel
        arguments:
          Google Calendar ID
          Discord Channel
        """
        channel = ctx.message.channel
        user = ctx.message.author
        if not sub_chan:
            await channel.send("Could not find channel {}".format(channel))
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

    @cal.command()
    async def auth_token(self, ctx, *, auth_token : str):
        """Submits an auth_token from Google, used while linking a Calendar"""
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
