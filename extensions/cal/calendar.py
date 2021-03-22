"""
Cog for Calendar Command
"""

import logging
from pathlib import Path
from queue import PriorityQueue
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from datafile import Data,DataFile
from dateutil import tz
from dateutil.tz import tzutc
import discord
from discord.ext import commands, tasks
import pyrfc3339 as rfc3339
from .google_calendar import GoogleCalendar, CalendarEvent
log = logging.getLogger('CalendarCog')

@dataclass(order=True)
class Subscription(Data):
    """Subscription Storage Dataclass"""
    calendar_id: str
    user_id: int
    channel_id: int
    guild_id: int

    def events(self, refresh_token):
        calendar = GoogleCalendar(calendar_id=self.calendar_id, refresh_token=refresh_token)
        now = datetime.utcnow().replace(tzinfo=tzutc())
        return [Event.from_calendar_event(x, subscription=self) for x in
                calendar.events(time_min=now, time_max=(now + timedelta(days=7)))]

@dataclass
class User(Data):
    """User Storage Dataclass"""
    user_id: int
    refresh_token: str = None

@dataclass
class Event(CalendarEvent,Data):
    """Event Storage Dataclass"""
    subscription: Subscription = None

    @classmethod
    def from_calendar_event(cls, event : CalendarEvent, **kwargs):
        return cls(**asdict(event), **kwargs)

@dataclass
class CalendarData(DataFile):
    """Calendar Data Storage"""
    summary_day: Optional[int] = None
    summary_hour: Optional[int] = None
    users: Dict[int, User] = field(default_factory=dict)
    subscriptions: List[Subscription] = field(default_factory=list)

@dataclass(order=True)
class CalendarQueueItem:
    """Sets Calendar Queue Priority"""
    time: datetime
    item: Event = field(compare=False)

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
        # pylint: disable=no-member
        self.tick.start()

    def set_next_execution(self):
        #execute once an hour, or sooner if we have an event coming up
        next_execution = datetime.utcnow().replace(tzinfo=tzutc(),minute=0,second=0) \
            + timedelta(hours=1)
        if not self.events.empty():
            peek = self.events.queue[0]
            next_execution = min(next_execution, peek.time)
            log.debug("Next Reminder: %s", rfc3339.generate(peek.time))
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
        return '{dt:%a}, {dt.day} {dt:%b} {dt:%H}:{dt:%M}'.format(dt=d_t)

    def event_to_embed(self, event) -> discord.Embed:
        event_tz = tz.gettz(event.calendar_tz)
        embed = discord.Embed.from_dict({
            "title": event.title,
            "description": event.description,
            "timestamp": event.start.timestamp()
            })
        if event.start:
            time = self.dtf(event.start.astimezone(event_tz))
            embed.add_field(name="Start", value=time, inline=True)
        if event.end:
            time = self.dtf(event.end.astimezone(event_tz))
            embed.add_field(name="End", value=time, inline=True)
        return embed

    async def chime(self):
        now = datetime.utcnow().replace(tzinfo=tzutc())
        while not self.events.empty():
            peek = self.events.queue[0]
            next_reminder = min(peek.time)
            if now >= next_reminder:
                event = self.events.get().item
                event.reminders.remove(next_reminder)
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

        for subscription in self.data.subscriptions:
            if channel_id and channel_id != subscription.channel_id:
                continue
            calendar_user = self.data.users.get(subscription.user_id)
            for event in sorted(subscription.events(calendar_user.refresh_token),
                    key=lambda x: x.start):
                log.debug("Summary event found for channel %s", event.subscription.channel_id)
                event_tz = tz.gettz(event.timezone)
                period = "{}".format(self.dtf(event.start.astimezone(event_tz)))
                if event.end:
                    if event.end == event.start + timedelta(days=1):
                        # All day event, one day. Let's assume this event ends EOD
                        event_end = event.end - timedelta(seconds=1)
                        period = "{}".format(self.dtf(event_end.astimezone(event_tz)))
                    else:
                        period = "{} to {}".format(self.dtf(event.start.astimezone(event_tz)),
                            self.dtf(event.end.astimezone(event_tz)))
                embed = embeds.setdefault(subscription.channel_id, embed.copy())
                embed.add_field(name=event.title,value=period, inline=True)
        return embeds

    def collect_next_events(self):
        self.events.queue.clear()
        for subscription in self.data.subscriptions:
            calendar_user = self.data.users.get(subscription.user_id)
            for event in subscription.events(calendar_user.refresh_token):
                for reminder in event.reminders:
                    self.events.put(CalendarQueueItem(time=reminder,item=event))

    @commands.group()
    async def cal(self, ctx):
        """
        Calendar Commands
        """

    @cal.group()
    async def debug(self, ctx):
        """Calendar Debug Commands"""

    @debug.command()
    @commands.is_owner()
    async def dump(self, ctx):
        """
        Outputs debug information
        """
        next_execution = "None scheduled"
        if self.next_execution:
            next_execution = rfc3339.generate(self.next_execution)
        now = datetime.utcnow().replace(tzinfo=tzutc())
        now = "{}, DOW {}, HR {}".format(rfc3339.generate(now), now.weekday(), now.hour)
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
            "{}\n"
            "```").format(
            now,
            next_execution,
            summary,
            self.events.qsize(),
            "\n".join(["  {}".format(x) for x in subscriptions]),
            )
        await ctx.channel.send(message)
        for queue_event in self.events.queue:
            await ctx.channel.send("```{}```".format(queue_event))

    @debug.command()
    @commands.is_owner()
    async def summary(self, ctx, sub_chan : discord.TextChannel):
        for _, embed in self.summary_embeds(sub_chan.id).items():
            await ctx.channel.send(embed=embed)

    @cal.command()
    async def events(self, ctx):
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
            subscription = Subscription(calendar_id=calendar_id, user_id=user.id,
                    channel_id=sub_chan.id, guild_id=channel.guild.id)
            if subscription in self.data.subscriptions:
                await channel.send("Already subscribed!")
                return
            self.data.subscriptions.append(subscription)
            self.data.save()
            await channel.send("Subscribed {} to {}".format(sub_chan, calendar.info.title))

    @cal.command()
    async def unsubscribe(self, ctx, calendar_id : str, sub_chan : discord.TextChannel):
        """
        Unsubscribes a Google Calendar from a Discord Channel
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
            await channel.send("Could not find user")
            return
        subscription = Subscription(calendar_id=calendar_id, user_id=user.id,
                channel_id=sub_chan.id, guild_id=channel.guild.id)
        if subscription not in self.data.subscriptions:
            await channel.send("Could not find subscription")
            return
        self.data.subscriptions.remove(subscription)
        self.data.save()
        await channel.send("Unsubscribed {} from {}".format(sub_chan, calendar_id))

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
