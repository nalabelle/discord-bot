from .status import Status


async def setup(bot):
    cog = Status(bot)
    await bot.add_cog(cog)


async def teardown(bot):
    await bot.remove_cog("Status")
