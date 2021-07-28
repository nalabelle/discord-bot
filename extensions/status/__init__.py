from .status import Status

def setup(bot):
    cog = Status(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Status')

