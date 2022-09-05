async def setup(bot):
    from .weather import Weather

    await bot.add_cog(Weather(bot))


async def teardown(bot):
    await bot.remove_cog("Weather")
