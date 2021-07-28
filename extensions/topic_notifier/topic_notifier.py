import discord
import asyncio
from discord.ext import commands

class TopicNotifier(commands.Cog):
    """ Announces topic changes """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before : discord.TextChannel,
            after : discord.TextChannel) -> None:
        old_topic = before.topic
        new_topic = after.topic
        if old_topic != new_topic:
            message = '_Topic changed from_ "{}" _to_ "{}".'.format(old_topic, new_topic)
            await after.send(content=message)

