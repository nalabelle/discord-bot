from .channel_notifier import ChannelNotifier

def setup(bot):
    cog = ChannelNotifier(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('ChannelNotifier')

