import sys,os
import asyncio
import discord
from discord.ext import commands
import geocoder
import forecastio
import datetime

try:
  FORECAST_API_KEY = os.environ['FORECAST_API_KEY']
  GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
except KeyError:
  print("Please set the FORECAST_API_KEY and GOOGLE_MAP_API_KEY env variables before running")
  sys.exit(1)

class Weather:
  """ Weather commands """

  def __init__(self, bot):
        self.bot = bot

  @commands.command(pass_context=True,description='Give me a location, get the weather')
  @asyncio.coroutine
  def weather(self, ctx, *, location : str):
    channel = ctx.message.channel
    try:
      yield from self.bot.send_typing(channel)
      loc = geocoder.google(location)
      forecast = forecastio.load_forecast(FORECAST_API_KEY, loc.lat, loc.lng, units='si')
      messages = []
      cur = forecast.currently()
      utc_dt = cur.time.strftime('%Y-%m-%d %H:%M UTC')
      messages.append('__{}__ `@{}`'.format(loc.address, utc_dt))
      messages.append('**Currently**: {} {}. {} {}'.format(
        self.icon_image(cur.icon), cur.summary,
        forecast.minutely().summary, forecast.hourly().summary))
      messages.append('**Temp**: {:,g}°C ({:,g}°F) **Feels Like**: {:,g}°C ({:,g}°F)'.format(
        round(cur.temperature,1), self.freedom_temp(cur.temperature),
        round(cur.apparentTemperature,1), self.freedom_temp(cur.apparentTemperature)))
      messages.append('**Humidity**: {:,g}%'.format(round(cur.humidity * 100, 0)))
      messages.append('**Chance of Rain**: {:,g}%'.format(round(cur.precipProbability * 100, 0)))
      messages.append('**Wind**: {} {:,g} kph ({:,g} freedom units)'.format(
        self.bearing(cur.windBearing), self.sensible_speed(cur.windSpeed),
        self.freedom_speed(cur.windSpeed)))
      if len(forecast.alerts()) > 0:
        for alert in forecast.alerts():
          messages.append('__**{}**__: {}: {}'.format(alert.severity.title(), alert.title, alert.uri))
      yield from self.bot.say('{}'.format("\n".join(messages)))
    except Exception as e:
      yield from self.bot.say('I broke! 😭 {}'.format(str(e)))
      pass

  def sensible_speed(self, speed_ms):
    """Given speed in meters/second returns kilometers/hour"""
    return round(speed_ms * 3.6, 2)

  def freedom_speed(self, speed_ms):
    """Given speed in meters/second returns miles/hour"""
    return round(speed_ms * 3.6 / 1.609344, 0)

  def freedom_temp(self, degrees_c):
    """Given temperature in C, returns F"""
    return round(degrees_c * 9 / 5 + 32, 0)

  def icon_image(self, desc):
    if not desc:
      return '⁉'
    if desc == 'clear-day':
      return '🌞'
    if desc == 'clear-night':
      return '🌚'
    if desc == 'rain':
      return '☔'
    if desc == 'snow':
      return '⛄'
    if desc == 'sleet':
      return '🌨'
    if desc == 'wind':
      return '🍃'
    if desc == 'fog':
      return '🌁'
    if desc == 'cloudy':
      return '☁'
    if desc == 'partly-cloudy-day':
      return '⛅'
    if desc == 'partly-cloudy-night':
      return '🌛'
    return '⁉'

  def bearing(self, degrees):
      bearing = degrees
      if degrees >= 348.75 or degrees <= 11.25:
          bearing = "N"
      elif degrees > 11.25 and degrees < 33.75:
          bearing = "NNE"
      elif degrees >= 33.75 and degrees <= 56.25:
          bearing = "NE"
      elif degrees > 56.25 and degrees < 78.75:
          bearing = "ENE"
      elif degrees >= 78.75 and degrees <= 101.25:
          bearing = "E"
      elif degrees > 101.25 and degrees < 123.75:
          bearing = "ESE"
      elif degrees >= 123.75 and degrees <= 146.25:
          bearing = "SE"
      elif degrees > 146.25 and degrees < 168.75:
          bearing = "SSE"
      elif degrees >= 168.75 and degrees <= 191.25:
          bearing = "S"
      elif degrees > 191.25 and degrees < 213.75:
          bearing = "SSW"
      elif degrees >= 213.75 and degrees <= 236.75:
          bearing = "SW"
      elif degrees > 236.75 and degrees < 258.75:
          bearing = "WSW"
      elif degrees >= 258.75 and degrees <= 281.25:
          bearing = "W"
      elif degrees > 281.25 and degrees < 303.75:
          bearing = "WNW"
      elif degrees >= 303.75 and degrees <= 326.25:
          bearing = "NW"
      elif degrees > 326.25 and degrees < 348.75:
          bearing = "NNW"
      return bearing
