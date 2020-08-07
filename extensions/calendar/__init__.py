from .calendar import Calendar

def setup(bot):
    cog = Calendar(bot)
    bot.add_cog(cog)

def teardown(bot):
    cog = bot.get_cog('Calendar')
    cog.tick.stop()
    bot.remove_cog('Calendar')

