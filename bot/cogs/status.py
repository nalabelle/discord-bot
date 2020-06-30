import discord
import asyncio
from discord.ext import commands
from ext import custom_permissions
from dataclasses import dataclass
from services.config import Data

@dataclass
class StatusData(Data):
    action: str = 'playing'
    status: str = 'with gear oil'

class Status(commands.Cog):
    """ Now Playing """

    def __init__(self, bot):
        self.bot = bot
        self.data = StatusData()
        self.data.load()

    async def set_initial_status(self):
        function = getattr(self, self.data.action)
        await function(self.data.status)

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def status(self, ctx, action : str, status : str):
        self.data.action = action
        self.data.status = status
        self.data.save()

        function = getattr(self, action)
        await function(status)

    async def playing(self, status : str):
        await self.bot.change_presence(activity=discord.Game(name=status))

    async def streaming(self, status : str):
        await self.bot.change_presence(activity=discord.Streaming(name=status))

    async def watching(self, status : str):
        await self.bot.change_presence(activity=discord.Activity(
            name=status,
            type=discord.enums.ActivityType.watching
            ))

    async def listening(self, status : str):
        if status.startswith("to"):
            status = status[2:]
        await self.bot.change_presence(activity=discord.Activity(
            name=status,
            type=discord.enums.ActivityType.listening
            ))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_initial_status()

def setup(bot):
    cog = Status(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Status')

