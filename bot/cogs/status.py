import discord
from discord.ext import commands
from lib import custom_permissions

class Status(commands.Cog):
    """ Now Playing """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def playing(self, ctx, *, status : str):
        await self.bot.change_presence(activity=discord.Game(name=status))

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def streaming(self, ctx, *, status : str):
        await self.bot.change_presence(activity=discord.Streaming(name=status))

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def watching(self, ctx, *, status : str):
        await self.bot.change_presence(activity=discord.Activity(
            name=status,
            type=discord.enums.ActivityType.watching
            ))

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def listening(self, ctx, *, status : str):
        if status.startswith("to"):
            status = status[2:]
        await self.bot.change_presence(activity=discord.Activity(
            name=status,
            type=discord.enums.ActivityType.listening
            ))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name="with gear oil"))

