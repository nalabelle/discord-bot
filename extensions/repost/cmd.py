import logging
import discord
from discord.ext import commands
from pathlib import Path
from .repost import Repost,RepostData

log = logging.getLogger('extRepost')

class RepostCommand(commands.Cog, name="Repost"):
    def __init__(self, bot):
        self.bot = bot
        path = str(Path(self.bot.data_path, 'repost.yml'))
        self.data = RepostData().from_yaml(path=path)
        self.listen_channels = dict()
        self.load_channels()
        log.info("Loaded {} channels".format(len(self.listen_channels)))

    def load_channels(self):
        for r in self.data.subscriptions:
            source = r.source_channel
            repost_list = self.listen_channels.get(source, list())
            if r.dest_channel not in repost_list:
                repost_list.append(r.dest_channel)
                self.listen_channels[source] = repost_list

    @commands.command()
    @commands.has_guild_permissions(manage_webhooks=True)
    async def repost(self, ctx, source: discord.TextChannel, dest: discord.TextChannel):
        r = Repost(source_channel = source.id, dest_channel = dest.id)
        if r in self.data.subscriptions:
            await ctx.message.channel.send('Already subscribed'.format(source, dest))
        else:
            self.data.subscriptions.append(r)
            self.data.save()
            self.load_channels()
            await ctx.message.channel.send('Subscribed {} to {}'.format(source, dest))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.bot.user.id == message.author.id:
            return True
        r = self.listen_channels.get(message.channel.id)
        log.debug("Checking for channel {}".format(r))
        if r is not None:
            for channel in r:
                log.debug("Posting to channel {}".format(channel))
                embed = discord.Embed.from_dict({
                    "description": message.content,
                    "url": message.jump_url
                    })
                author_name = message.author.nick or message.author.name
                embed.set_author(name=author_name,url=message.jump_url,icon_url=message.author.avatar_url)
                chan = discord.utils.get(self.bot.get_all_channels(),
                        id=channel)
                await chan.send(embed=embed)

def setup(bot):
    bot.add_cog(RepostCommand(bot))

def teardown(bot):
    bot.remove_cog('Repost')

