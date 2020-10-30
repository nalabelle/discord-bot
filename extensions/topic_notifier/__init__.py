from .topic_notifier import TopicNotifier

def setup(bot):
    cog = TopicNotifier(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('TopicNotifier')

