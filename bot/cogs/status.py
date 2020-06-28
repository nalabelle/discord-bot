import discord
import asyncio
from discord.ext import commands
from ext import custom_permissions
from services.config import Config

class Status(commands.Cog):
    """ Now Playing """

    def __init__(self, bot):
        self.bot = bot
        config = self.bot.config.get('presence', dict())
        self.action = config.get('action', 'playing')
        self.status = config.get('status', 'with gear oil')

    def dump(self):
        return {
                "action": self.action,
                "status": self.status
                }

    async def set_initial_status(self):
        function = getattr(self, self.action)
        await function(self.status)

    @commands.command(hidden=True)
    @custom_permissions.is_owner_or_admin()
    async def status(self, ctx, action : str, status : str):
        self.action = action
        self.status = status
        self.bot.config.set('presence', self.dump())
        self.bot.config.save_config()

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

