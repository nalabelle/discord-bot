import dateutil
import dateutil.parser
import yaml
import discord
from discord.ext import commands
from .service import WeatherService

class Weather(commands.Cog):
    """ Weather commands """

    def __init__(self, bot):
        self.bot = bot
        self.weather = WeatherService()

    @commands.command(description='Give me a location, get the weather')
    async def weather(self, ctx, *, location : str):
        channel = ctx.message.channel
        weather_embed = None
        async with channel.typing():
            weather_embed = self.get_weather(location)
        if weather_embed:
            await channel.send(embed=weather_embed)

    def get_weather(self, location):
        weather = self.weather.get_weather(location)

        currently_field = '{} {}.'.format(weather.current_icon, weather.current_summary)
        if weather.hourly_summary:
            currently_field += ' {}'.format(weather.hourly_summary)

        if weather.daily_summary:
            currently_field += ' {}'.format(weather.daily_summary)

        temp_field = '{:,g}°C ({:,g}°F)'.format(weather.current_temp.c, weather.current_temp.f)

        temp_feels_field = '{:,g}°C ({:,g}°F)'.format(weather.feels_like.c, weather.feels_like.f)

        temp_high_low_field = '{:,g}°C ({:,g}°F)/{:,g}°C ({:,g}°F)'.format(
                weather.daily_temp.high.c, weather.daily_temp.high.f,
                weather.daily_temp.low.c, weather.daily_temp.low.c)

        humidity_field = '{:,g}%'.format(weather.humidity)

        precip_field = '{:,g}%'.format(weather.precip)
        wind_field = '{} {:,g} kph ({:,g} freedom units)'.format(
                weather.wind.bearing, weather.wind.kph, weather.wind.mph)

        utc_time = dateutil.parser.parse(weather.utc_time)
        utc_formatted = utc_time.strftime('%Y-%m-%d %H:%M UTC')
        local_time = utc_time.astimezone(dateutil.tz.gettz(weather.local_timezone))
        local_formatted = local_time.strftime('%Y-%m-%d %H:%M {}'.format(weather.local_timezone))

        time_info = '{} \u2022 Local: {}'.format(utc_formatted, local_formatted)
        darksky_attribution = '[Powered by Dark Sky](https://darksky.net/poweredby/)'
        description = '{}\n{}'.format(time_info, darksky_attribution)

        weather_embed = discord.Embed.from_dict({
            "title": weather.location,
            "description": description,
            "timestamp": weather.utc_time,
            "fields": [
                {
                    "name": '**Currently**',
                    "value": currently_field,
                    "inline": True
                },
                {
                    "name": '**Temp**',
                    "value": temp_field,
                    "inline": True
                },
                {
                    "name": '**Feels Like**',
                    "value": temp_feels_field,
                    "inline": True
                },
                {
                    "name": '**High/Low**',
                    "value": temp_high_low_field,
                    "inline": True
                },
                {
                    "name": '**Humidity**',
                    "value": humidity_field,
                    "inline": True
                },
                {
                    "name": '**Precipitation**',
                    "value": precip_field,
                    "inline": True
                },
                {
                    "name": '**Wind**',
                    "value": wind_field,
                    "inline": True
                },
                ],
            })

        alert_text = ''
        for alert in weather.alerts:
            alert_text = alert_text + '__**{}**__: {}: {}\n'.format(
                    alert.severity, alert.title, alert.uri)

        if len(alert_text) > 0:
            weather_embed.add_field(
                name='**Alerts**',
                value=alert_text,
                inline=True
                )

        return weather_embed

