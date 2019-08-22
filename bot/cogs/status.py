import discord
from discord.ext import commands

class Status(commands.Cog):
    """ Now Playing """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def playing(self, ctx, *, status : str):
        if await self.check_permissions(ctx):
            await self.bot.change_presence(activity=discord.Game(name=status))

    @commands.command(hidden=True)
    async def streaming(self, ctx, *, status : str):
        if await self.check_permissions(ctx):
            await self.bot.change_presence(activity=discord.Streaming(name=status))

    @commands.command(hidden=True)
    async def watching(self, ctx, *, status : str):
        if await self.check_permissions(ctx):
            await self.bot.change_presence(activity=discord.Activity(
                name=status,
                type=discord.enums.ActivityType.watching
                ))

    @commands.command(hidden=True)
    async def listening(self, ctx, *, status : str):
        if status.startswith("to"):
            status = status[2:]
        if await self.check_permissions(ctx):
            await self.bot.change_presence(activity=discord.Activity(
                name=status,
                type=discord.enums.ActivityType.listening
                ))

    # If I could unwrap the decorators, I could probably call these directly
    # from discord.ext.commands.core...
    async def check_permissions(self, ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        permissions = ch.permissions_for(ctx.channel.author)
        if 'manage_webhooks' in permissions:
            return True
        await ctx.channel.send('You can\'t tell me what to do!')
        return False

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="with gear oil"))

