from .config import ConfigReload

def setup(bot):
    bot.add_cog(ConfigReload(bot))

def teardown(bot):
    bot.remove_cog('ConfigReload')

