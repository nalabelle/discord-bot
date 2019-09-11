import discord
from discord.ext import commands
from services.contest import Contest
from lib import custom_permissions

class DrawingContest(commands.Cog):
    """Drawing Contest Commands"""

    def __init__(self, bot):
        self.bot = bot
        self.contest = Contest()

    @commands.group(name="draw")
    async def draw(self, ctx):
        """Drawing Contest Commands"""

    @draw.group(name="prompt",invoke_without_command=True)
    async def prompt(self, ctx):
        """Get a drawing prompt"""
        channel = ctx.message.channel
        prompt = self.contest.get_prompt()
        if prompt is None:
            await channel.send('Add some! I\'m all out!')
        else:
            await channel.send('Draw: **{}**!'.format(prompt))

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

