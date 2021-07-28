import discord
import asyncio
from discord.ext import commands

class ChannelNotifier(commands.Cog):
    """ Announces channel name changes """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before : discord.TextChannel,
            after : discord.TextChannel) -> None:
        old_name = before.name
        new_name = after.name
        if old_name != new_name:
            message = '_Channel name changed from_ "{}" _to_ "{}".'.format(old_name, new_name)
            await after.send(content=message)

