from discord.ext import commands
from .repost import Repost,RepostData

class RepostCommand(commands.Cog, name=="Repost"):
    def __init__(self, bot):
        self.bot = bot
        path = str(Path(self.bot.data_path, 'repost.yml'))
        self.data = RepostData().from_yaml(path=path)
        self.listen_channels = dict()
        self.load_channels()

    def load_channels(self):
        for r in self.data.subscriptions:
            source = r.source_channel
            repost_list = self.listen_channels.get(source, list())
            if r.dest_channel not in repost_list:
                repost_list.append(r.dest_channel)
                self.listen_channels.set(source, repost_list)

    @commands.command()
    @commands.has_guild_permissions(manage_webhooks=True)
    async def repost(self, ctx, source: discord.TextChannel, dest: discord.TextChannel):
        r = Repost(source_channel = source.id, dest_channel = dest.id)
        if r in self.data.subscriptions:
            await ctx.message.channel.send('Already subscribed'.format(source, dest)
        else:
            self.data.subscriptions.append(r)
            self.data.save()
            self.load_channels()
            await ctx.message.channel.send('Subscribed {} to {}'.format(source, dest)

    async def on_message(self, message: discord.Message):
        r = self.listen_channels.get(message.channel.id)
        if r is not None:
            cache_channels = list()
            for channel in r:
                content = message.content
                content = content + '\n```{}```'.format(message.jump_url)
                chan = discord.utils.get(self.bot.get_all_channels(),
                        id=r.dest_channel)
                chan.send(content)
                cache_channels.append(channel)
            self.listen_channels.set(message.channel.id, cache_channels)

def setup(bot):
    bot.add_cog(RepostCommand(bot))

def teardown(bot):
    bot.remove_cog('Repost')

