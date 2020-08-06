from .bot_admin import ExtensionAdmin

def setup(bot):
    cog = ExtensionAdmin(bot)
    bot.add_cog(cog)

def teardown(bot):
    bot.remove_cog('BotAdmin')

