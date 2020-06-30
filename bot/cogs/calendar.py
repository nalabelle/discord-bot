import discord
import logging
from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import List, Dict
from discord.ext import commands, tasks
from services.google_calendar import GoogleCalendar
from services.config import Data
import dateutil.parser
import dateutil.tz
from datetime import datetime, timedelta

log = logging.getLogger('CalendarCog')

@dataclass
class User(Data):
    user_id: int
    refresh_token: str = None

@dataclass
class Event(Data):
    datetime: datetime
    title: str
    description: str

@dataclass
class Subscription(Data):
    calendar_id: str
    user_id: int
    channel_id: int
    guild_id: int

@dataclass
class CalendarData(Data):
    users: Dict[int, User] = field(default_factory=dict)
    subscriptions: List[Subscription] = field(default_factory=list)

class Calendar(commands.Cog):
    """ Calendar commands """

    def __init__(self, bot):
        self.bot = bot
        self.events = PriorityQueue()
        self.awaiting_user_auth = {}
        self.data = CalendarData()
        self.data.load()

    @commands.Cog.listener()
    async def on_ready(self):
        self.time = datetime.strptime('2020-06-28 12:00:00 -0700', '%Y-%m-%d %H:%M:%S %z')
        await self.print_calendar_week.start()

    @tasks.loop(count=1)
    async def print_calendar_week(self):
        await discord.utils.sleep_until(self.time)
        return
        calendars = self.get_all_calendars()
        users = self.data.users
        events = []
        for (calendar_id, calendar) in calendars:
            log.warn(calendar)
            user = users.get(calendar["user"])
            if user:
                refresh_token = user["refresh_token"]
                cal = GoogleCalendar(calendar_id=calendar_id, refresh_token=refresh_token)
                time_min = datetime.utcnow().isoformat('T') + "Z"
                time_max = datetime.utcnow() + timedelta(days=7)
                time_max = time_max.isoformat('T') + "Z"
                log.warn(time_min)
                #items = cal.list_events(timeMin=datetime.datetime.utcnow().isoformat('T'))
                items = cal.list_events(
                        orderBy="startTime", timeMin=time_min,
                        timeMax=time_max,singleEvents=True)["items"]
                log.warn(items)
                for item in items:
                    events.append("{} @ {}".format(item["summary"], item["start"]["dateTime"]))

        chid = 700249856039452774
        out_chan = discord.utils.get(self.bot.get_all_channels(), id=chid)
        await out_chan.send("{}".format("\n".join(events)))
#

#    @commands.command()
#    async def calendars(self, ctx):
#        calendars = self.get_all_calendars()
#        await ctx.channel.send("{}".format(",".join(calendars)))

    def get_all_calendars(self):
        calendars = []
        for subscription in self.data.subscriptions:
            calendars.append(subscription.calendar_id)
        return calendars

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

def setup(bot):
    cog = Calendar(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Calendar')

