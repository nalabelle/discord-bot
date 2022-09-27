"""
Weather Commands
"""

import logging

import discord
import forecastio
import geocoder
from discord import app_commands
from discord.ext import commands
from file_secrets import secret

from extensions.weather.models import WeatherData

log = logging.getLogger("Weather")


class Weather:
    """Fetches the weather and formats it for Discord"""

    darksky_attribution = "Powered by Dark Sky"

    @staticmethod
    def _location_to_data(location: str) -> WeatherData:
        """Takes a location string and returns a WeatherData object"""
        loc = geocoder.google(location, key=secret("google_api_key"))
        # log.debug("%s", loc)
        forecast = forecastio.load_forecast(
            secret("forecast_api_key"), loc.lat, loc.lng, units="si"
        )
        # log.debug("%s", forecast.json)
        return WeatherData.from_forecast(loc.address, forecast)

    @staticmethod
    def for_location(location: str) -> discord.Embed:
        """Takes a location string and returns a formatted Discord Embed"""
        return Weather._format_weather(Weather._location_to_data(location))

    @staticmethod
    def _format_weather(weather: WeatherData) -> discord.Embed:
        """Takes WeatherData and returns a formatted Discord Embed"""
        weather_embed = discord.Embed.from_dict(
            {
                "title": weather.location,
                "footer": {
                    "text": " \u2022 ".join(
                        [
                            weather.time.utc_formatted(),
                            weather.time.local_time_formatted(),
                            Weather.darksky_attribution,
                        ]
                    )
                },
                "timestamp": weather.time.time.isoformat(),
                "fields": [
                    {
                        "name": "**Currently**",
                        "value": " ".join(
                            [
                                f"{weather.current_icon} {weather.current_summary}.",
                                weather.hourly_summary,
                                weather.daily_summary,
                            ]
                        ),
                        "inline": False,
                    },
                    {
                        "name": "**Temp**",
                        "value": weather.current_temp.formatted(),
                        "inline": True,
                    },
                    {
                        "name": "**Feels Like**",
                        "value": weather.feels_like.formatted(),
                        "inline": True,
                    },
                    {
                        "name": "**High/Low**",
                        "value": "/".join(
                            [
                                weather.daily_temp.high.formatted(),
                                weather.daily_temp.low.formatted(),
                            ]
                        ),
                        "inline": True,
                    },
                    {"name": "**Humidity**", "value": f"{weather.humidity:,g}%", "inline": True},
                    {
                        "name": "**Precipitation**",
                        "value": f"{weather.precip:,g}%",
                        "inline": True,
                    },
                    {
                        "name": "**Wind**",
                        "value": " ".join(
                            [
                                f"{weather.wind.bearing}",
                                f"{weather.wind.speed.kph():,g} kph",
                                f"({weather.wind.speed.mph():,g} freedom units)",
                            ]
                        ),
                        "inline": True,
                    },
                ],
            }
        )

        alert_text = "\n".join(
            [
                f"__**{alert.severity}**__: [{alert.title}]({alert.uri})"
                for alert in weather.alerts
            ]
        )
        if alert_text:
            weather_embed.add_field(name="**Alerts**", value=alert_text, inline=False)

        return weather_embed


class WeatherCommand(commands.Cog, name="Weather"):
    """Weather commands"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.autocomplete()
    async def weather(self, interaction: discord.Interaction, location: str):
        """Gets the weather for the specified location

        Args:
          location:
            The location to get the weather for
        """
        weather_embed = Weather.for_location(location)
        await interaction.response.send_message(embed=weather_embed)


async def setup(bot):
    """Cog creation"""
    await bot.add_cog(WeatherCommand(bot))


async def teardown(bot):
    """Cog teardown"""
    await bot.remove_cog("Weather")
