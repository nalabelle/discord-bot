"""
Discord Cog for Repost
"""

import logging
import datetime
from pathlib import Path
import discord
from discord.ext import commands
from .repost import Repost,RepostData

log = logging.getLogger('extRepost')

class RepostCommand(commands.Cog, name="Repost"):
    """Discord Cog for Repost"""
    def __init__(self, bot):
        self.bot = bot
        path = str(Path(self.bot.data_path, 'repost.yml'))
        self.data = RepostData().from_yaml(path=path)
        self.listen_channels = dict()
        self.load_channels()
        log.info("Loaded %d channels", len(self.listen_channels))

    def load_channels(self):
        """Loads the subscription channels from config into memory"""
        for sub in self.data.subscriptions:
            source = sub.source_channel
            repost_list = self.listen_channels.get(source, list())
            if sub.dest_channel not in repost_list:
                repost_list.append(sub.dest_channel)
                self.listen_channels[source] = repost_list

    @commands.command()
    @commands.has_guild_permissions(manage_webhooks=True)
    async def repost(self, ctx, source: discord.TextChannel, dest: discord.TextChannel):
        """Link channels to repost from one to the other"""
        repost_channel = Repost(source_channel = source.id, dest_channel = dest.id)
        if repost_channel in self.data.subscriptions:
            await ctx.message.channel.send('Already subscribed')
        else:
            self.data.subscriptions.append(repost_channel)
            self.data.save()
            self.load_channels()
            await ctx.message.channel.send('Subscribed {} to {}'.format(source, dest))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """new message event handler"""
        if self.bot.user.id == message.author.id:
            return True
        repost_channels = self.listen_channels.get(message.channel.id)
        if repost_channels is None:
            return
        for channel in repost_channels:
            log.debug("Posting to channel %s", channel)
            if len(message.embeds) > 0:
                log.debug("Message has embed %s", message.embeds)
            embed = discord.Embed.from_dict({
                "description": message.content,
                "url": message.jump_url
                })
            author_name = message.author.nick or message.author.name
            embed.set_author(name=author_name,url=message.jump_url,
                    icon_url=message.author.avatar_url)
            chan = discord.utils.get(self.bot.get_all_channels(), id=channel)
            await chan.send(embed=embed)
            for embed_copy in message.embeds:
                await chan.send(embed=embed_copy)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """message deleted event handler"""
        if self.bot.user.id == message.author.id:
            return True

        repost_channels = self.listen_channels.get(message.channel.id)
        if repost_channels is None:
            return
        search_interval = datetime.timedelta(hours=1)
        created_at = message.created_at
        search_start = created_at - search_interval
        search_end = created_at + search_interval
        for channel in repost_channels:
            log.debug("Deleting from channel %s", channel)
            chan = discord.utils.get(self.bot.get_all_channels(),
                    id=channel)
            async for chan_message in chan.history(before=search_end, after=search_start):
                for embed in chan_message.embeds:
                    if embed.url == message.jump_url:
                        log.debug("Embed URL match, deleting message %s", embed.url)
                        await chan_message.delete()

def setup(bot):
    """Cog creation"""
    bot.add_cog(RepostCommand(bot))

def teardown(bot):
    """Cog teardown"""
    bot.remove_cog('Repost')
