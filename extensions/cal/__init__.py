from .calendar import Calendar

def setup(bot):
    cog = Calendar(bot)
    bot.add_cog(cog)

def teardown(bot):
    cog = bot.get_cog('Calendar')
    cog.tick.cancel()
    bot.remove_cog('Calendar')
