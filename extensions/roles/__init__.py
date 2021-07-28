from .roles import Roles

def setup(bot):
    cog = Roles(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('Roles')

