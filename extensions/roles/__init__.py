from .roles import Roles


async def setup(bot):
    cog = Roles(bot)
    await bot.add_cog(cog)


async def teardown(bot):
    await bot.remove_cog("Roles")
