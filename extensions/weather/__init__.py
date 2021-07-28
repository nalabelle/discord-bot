def setup(bot):
    from .weather import Weather
    bot.add_cog(Weather(bot))

def teardown(bot):
    bot.remove_cog('Weather')

