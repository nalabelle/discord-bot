import discord
import logging
from discord.ext import commands, tasks
from services.google_calendar import GoogleCalendar
from services.config import Config
import dateutil.parser
import dateutil.tz
from datetime import datetime, timedelta

log = logging.getLogger('CalendarCog')
class Calendar(commands.Cog):
    """ Calendar commands """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config(path=bot.get_storage_path('calendar.yml'))
        self.awaiting_user_auth = {}

        if self.config.get('users') is None:
            self.config.set('users', users)

        if self.config.get('guilds') is None:
            self.config.set('guilds', {})

    @commands.Cog.listener()
    async def on_ready(self):
        self.time = datetime.strptime('2020-06-28 12:00:00 -0700', '%Y-%m-%d %H:%M:%S %z')
        await self.print_calendar_week.start()

    @tasks.loop(count=1)
    async def print_calendar_week(self):
        await discord.utils.sleep_until(self.time)
        calendars = self.get_all_calendars()
        users = self.config.get('users')
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
        guilds = self.config.get('guilds')
        for guild in guilds.values():
            for channel in guild.values():
                for calendar in channel.items():
                    calendars.append(calendar)
        return calendars

    @commands.command()
    async def subscribe(self, ctx, calendar_id : str, sub_chan : discord.TextChannel):
        channel = ctx.message.channel
        user = ctx.message.author.id
        users = self.config.get('users')
        guilds = self.config.get('guilds')
        if not sub_chan:
            await channel.send("Could not find channel {}".format(chan))
            return
        if user not in users:
            calendar = GoogleCalendar()
            url = calendar.get_auth_url()
            self.awaiting_user_auth[user] = calendar
            message = "Click the following link to authorize me to view your Google Calendars." \
                    "Once Done, use the auth_token command to submit the code it displays." \
                    "{}".format(url)
            await channel.send(message)
        else:
            refresh_token = users.get(user)['refresh_token']
            calendar = GoogleCalendar(calendar_id=calendar_id, refresh_token=refresh_token)
            info = calendar.get_info()
            guild = guilds.get(channel.guild.id)
            if guild:
                chan = guild.get(sub_chan.id)
                if chan:
                    cal = chan.get(info["id"])
                    if cal:
                        await chan.send("Already subscribed!")
                        return
                    else:
                        chan[info.id] = {"events": ["all", "weekly"]}
                else:
                    chan = {}
                    chan[info["id"]] = {"events": ["all", "weekly"]}
                    guild[sub_chan.id] = chan
            else:
                guild = {}
                chan = {}
                chan[info["id"]] = {"user": user.id, "events": ["all", "weekly"]}
                guild[sub_chan.id] = chan
                guilds[channel.guild.id] = guild
            await channel.send("Subscribed {} to {}".format(sub_chan, info['summary']))
            self.config.save_config()

    @commands.command()
    async def auth_token(self, ctx, *, auth_token : str):
        channel = ctx.message.channel
        user = ctx.message.author.id
        awaiting_auth = self.awaiting_user_auth.get(user)
        if not awaiting_auth:
            await channel.send("I don't have any auths open, maybe restart the subscription?")
            return
        refresh_token = awaiting_auth.submit_auth_code(auth_token)
        users = self.config.get('users')
        if user not in users:
            users[user] = {"refresh_token": refresh_token}
            self.config.save_config()
        await channel.send('authed')

def setup(bot):
    cog = Calendar(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Calendar')

