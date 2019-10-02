from datetime import datetime, timedelta
import discord
from discord.ext import tasks,commands
from services.contest import Contest
from ext import custom_permissions

class DrawingContest(commands.Cog):
    """Drawing Contest Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.contest = Contest()
        self._next_prompt = None
        self.prompt_timer.start()

    def cog_unload(self):
        self.prompt_timer.cancel()

    def set_timer(self, channel, days_to_wait=1, next_execution=None):
        now = datetime.now()
        if next_execution is None or next_execution < now:
            next_execution = now + timedelta(days=days_to_wait)
        self.contest.set_next_execution(\
                next_execution=next_execution.isoformat(' '),
                channel=channel.id,
                days=days_to_wait)
        self._next_prompt = {'channel': channel, 'time': next_execution, 'days': days_to_wait}
        return next_execution

    @tasks.loop(seconds=60)
    async def prompt_timer(self):
        if self._next_prompt is None:
            return
        time = self._next_prompt['time']
        channel = self._next_prompt['channel']
        days = self._next_prompt['days']
        if datetime.now() > time:
            self.set_timer(channel, days_to_wait=days)
            await self.say_prompt(channel)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        next_execution = self.contest.next_execution
        if next_execution is not None:
            channel = self.bot.get_channel(next_execution['channel'])
            dt = datetime.strptime(next_execution['time'], "%Y-%m-%d %H:%M:%S.%f")
            days = next_execution['days']
            if channel is not None and dt is not None:
                print("setting timer")
                self.set_timer(channel, next_execution=dt, days_to_wait=days)
            else:
                print("wtf {}".format(next_execution['channel']))

    async def say_prompt(self, channel):
        prompt = self.contest.get_prompt()
        if prompt is None:
            await channel.send('Add some! I\'m all out!')
        else:
            await channel.send('Draw: **{}**!'.format(prompt))

    @commands.group(name="draw")
    async def draw(self, ctx):
        """Drawing Contest Commands"""

    @draw.group(name="timer")
    async def timer(self, ctx):
        """Drawing Contest Timers"""

    @timer.command(description="Set the timer")
    @custom_permissions.is_owner_or_admin()
    async def set(self, ctx, *, phrase : str):
        channel = ctx.message.channel
        if phrase and not phrase.isdigit():
            phrase = None
        next_execution = self.set_timer(channel, days_to_wait=phrase)
        await channel.send('Draw timer started, will prompt at {}'.format(next_execution))

    @timer.command(description="Unset the timer")
    @custom_permissions.is_owner_or_admin()
    async def unset(self, ctx):
        channel = ctx.message.channel
        self.contest.set_next_execution(None)
        self._next_prompt = None
        await channel.send('Draw timer stopped')

    @draw.group(name="prompt",invoke_without_command=True)
    async def prompt(self, ctx):
        """Get a drawing prompt"""
        channel = ctx.message.channel
        await self.say_prompt(channel)

    @prompt.command(description='Add a drawing subject')
    async def add(self, ctx, *, phrase : str):
        channel = ctx.message.channel
        async with channel.typing():
            added = self.contest.add_prompt(phrase)
        if added:
            await channel.send('added "{}" to drawing prompts!'.format(phrase))
        else:
            await channel.send('sorry, I didn\'t understand that one.')

    @prompt.command(description='Dump drawing subjects',hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def dump(self, ctx):
        channel = ctx.message.channel
        prompts = self.contest.dump_prompts()
        shuffled_prompts = self.contest.dump_shuffled_prompts()
        if len(prompts) > 0:
            await channel.send('\n'.join(prompts))
            if len(shuffled_prompts) > 0:
                await channel.send('\n'.join(shuffled_prompts))
        else:
            await channel.send('I don\'t have any prompts yet!')

    @prompt.command(description='Shuffle drawing subjects',hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def shuffle(self, ctx):
        channel = ctx.message.channel
        async with channel.typing():
            self.contest.shuffle_prompts()
        await channel.send('Done!')

