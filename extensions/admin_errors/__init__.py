from .errors import Errors

def setup(bot):
    cog = Errors(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Errors')

