from .channel_notifier import ChannelNotifier


async def setup(bot):
    cog = ChannelNotifier(bot)
    await bot.add_cog(cog)


async def teardown(bot):
    await bot.remove_cog("ChannelNotifier")
