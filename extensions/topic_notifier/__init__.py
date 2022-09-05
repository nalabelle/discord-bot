from .topic_notifier import TopicNotifier


async def setup(bot):
    cog = TopicNotifier(bot)
    await bot.add_cog(cog)


async def teardown(bot):
    await bot.remove_cog("TopicNotifier")
