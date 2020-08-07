import discord
import asyncio
from pathlib import Path
from discord.ext import commands
from dataclasses import dataclass
from datafile import DataFile

@dataclass
class StatusData(DataFile):
    action: str = 'playing'
    status: str = 'with gear oil'

class Status(commands.Cog):
    """ Now Playing """

    def __init__(self, bot):
        self.bot = bot
        path = str(Path(self.bot.data_path, 'status.yml'))
        self.data = StatusData().from_yaml(path)

    async def set_initial_status(self):
        function = getattr(self, self.data.action)
        await function(self.data.status)

    @commands.command(hidden=True)
    @commands.check_any(commands.is_owner(), commands.has_guild_permissions(manage_webhooks=True))
    async def status(self, ctx, action : str, *, status : str):
        self.data.action = action
        self.data.status = status
        self.data.save()

        function = getattr(self, action)
        await function(status)

    async def playing(self, status : str):
        await self.bot.change_presence(activity=discord.Game(name=status))

    async def streaming(self, status : str):
        await self.bot.change_presence(activity=discord.Streaming(name=status,url="https://www.youtube.com/watch?v=uc6f_2nPSX8"))

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

