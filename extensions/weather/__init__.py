from .weather import Weather

def setup(bot):
    cog = Weather(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Weather')

