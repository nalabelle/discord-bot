"""
Discord Cog for Repost
"""
import datetime

import discord
from discord import app_commands
from discord.ext import commands

from extensions.repost.repost import (
    DATAFILE,
    LinkedChannel,
    RepostData,
    SourceChannel,
    log,
)


@app_commands.guild_only()
@app_commands.default_permissions(manage_guild=True)
class RepostCommand(app_commands.Group, name="repost"):
    """Repost commands"""

    def __init__(self, repost_data: RepostData):
        super().__init__()
        self.data = repost_data

    @app_commands.command()
    @app_commands.autocomplete()
    async def link(
        self,
        interaction: discord.Interaction,
        source: discord.TextChannel,
        linked_channel: discord.TextChannel,
    ):
        """Link channels to repost from one to the other"""
        source_id = SourceChannel(source.id)
        linked_id = LinkedChannel(linked_channel.id)
        if self.data.add_link(source=source_id, link=linked_id):
            await interaction.response.send_message(f"Linked <#{linked_id}> to <#{source_id}>")
        else:
            await interaction.response.send_message(
                f"<#{linked_id}> was already linked to <#{source_id}>"
            )

    @app_commands.command()
    @app_commands.autocomplete()
    async def unlink(
        self,
        interaction: discord.Interaction,
        source: discord.TextChannel,
        linked_channel: discord.TextChannel,
    ):
        """Remove a repost link between channels"""
        source_id = SourceChannel(source.id)
        linked_id = LinkedChannel(linked_channel.id)
        if self.data.remove_link(source=source_id, link=linked_id):
            await interaction.response.send_message(
                f"Unlinked <#{linked_id}> from <#{source_id}>"
            )
        else:
            await interaction.response.send_message(
                f"<#{linked_id} wasn't linked to <#{source_id}>"
            )


class RepostCog(commands.Cog, name="Repost"):
    def __init__(self, bot, repost_data: RepostData):
        self.bot = bot
        self.data = repost_data
        print(repost_data)

    def from_bot(self, msg: discord.Message):
        return self.bot.user.id == msg.author.id

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """new message event handler"""
        if self.from_bot(message):
            log.debug("self message")
            return
        log.debug(f"checking channels {self.data}")
        source_id = SourceChannel(message.channel.id)
        for channel in self.data.linked_channels(source_id):
            log.debug("Posting to channel %s", channel)
            chan = self.bot.get_channel(channel)
            author_name = message.author.nick or message.author.name
            embed = discord.Embed(
                description=f"Reposting from <#{source_id}>",
                url=message.jump_url,
                timestamp=message.created_at,
            ).set_author(
                name=author_name,
                url=message.jump_url,
                icon_url=message.author.display_avatar.url,
            )
            await chan.send(embed=embed)
            await chan.send(content=message.content)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """message deleted event handler"""
        if self.from_bot(message):
            return
        search_interval = datetime.timedelta(hours=1)
        created_at = message.created_at
        search_start = created_at - search_interval
        search_end = created_at + search_interval
        source_id = SourceChannel(message.channel.id)
        for channel in self.data.linked_channels(source_id):
            log.debug("Deleting from channel %s", channel)
            chan = self.bot.get_channel(channel)
            async for chan_message in chan.history(before=search_end, after=search_start):
                for embed in chan_message.embeds:
                    if embed.url == message.jump_url:
                        log.debug("Embed URL match, deleting message %s", embed.url)
                        await chan_message.delete()


# from discord_bot.config import DataFile


async def setup(bot):
    """Cog creation"""
    data = RepostData.from_yaml(bot.data / DATAFILE)
    await bot.add_cog(RepostCog(bot, data))
    bot.tree.add_command(RepostCommand(repost_data=data))


async def teardown(bot):
    """Cog teardown"""
    await bot.remove_cog("Repost")
