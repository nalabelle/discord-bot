def setup(bot):
    from .config import ConfigReload
    bot.add_cog(ConfigReload(bot))

def teardown(bot):
    bot.remove_cog('ConfigReload')

