import geocoder
import forecastio
import datetime
import logging
from dateutil import tz
from dataclasses import dataclass, field
from datafile import Data
from file_secrets import secret

log = logging.getLogger()

@dataclass
class Temp(Data):
    c: float
    f: float

@dataclass
class TempRange(Data):
    high: Temp
    low: Temp

@dataclass
class Wind(Data):
    bearing: str
    kph: float
    mph: float

@dataclass
class Alert(Data):
    severity: str
    title: str
    uri: str
 
@dataclass
class WeatherData(Data):
    location: str
    utc_time: str
    local_timezone: str
    current_summary: str
    current_icon: str
    current_temp: Temp
    feels_like: Temp
    daily_temp: TempRange
    humidity: int
    precip: int
    wind: Wind
    alerts: field(default_factory=set)

class WeatherService:
    """ Weather commands """

    def __init__(self):
        self.forecast_api_key = secret('forecast_api_key')
        self.google_api_key = secret('google_api_key')
        if not self.forecast_api_key:
            raise Error('Need forecast_api_key')
        if not self.google_api_key:
            raise Error('Need google_api_key')

    def get_weather(self, location_text):
        loc = self.geocode_location(location_text)
        if loc is None:
            raise Error('Could not find location')
        log.debug("got location {}".format(loc))
        forecast = self.get_forecast(loc.lat, loc.lng)
        cur = forecast.currently()
        day = forecast.daily().data[0]

        utc_time = cur.time.replace(tzinfo=tz.gettz('UTC'))
        local_timezone = forecast.json['timezone']
        utc_dt = utc_time.isoformat()

        weather = WeatherData.from_dict({
                "location": loc.address,
                "utc_time": utc_dt,
                "local_timezone": local_timezone,
                "current_summary": cur.summary,
                "current_icon": self.icon_image(cur.icon),
                "current_temp": {
                    "c": round(cur.temperature,1),
                    "f": self.freedom_temp(cur.temperature)
                    },
                "feels_like": {
                    "c": round(cur.apparentTemperature,1),
                    "f": self.freedom_temp(cur.apparentTemperature)
                    },
                "daily_temp": {
                    "high": {
                        "c": round(day.temperatureHigh,1),
                        "f": self.freedom_temp(day.temperatureHigh)
                        },
                    "low": {
                        "c": round(day.temperatureLow,1),
                        "f": self.freedom_temp(day.temperatureLow)
                        }
                    },
                "humidity": round(cur.humidity * 100, 0),
                "precip": round(cur.precipProbability * 100, 0),
                "wind": {
                    "bearing": self.bearing(cur.windBearing),
                    "kph": self.sensible_speed(cur.windSpeed),
                    "mph": self.freedom_speed(cur.windSpeed)
                    },
                "hourly_summary": forecast.minutely().summary,
                "daily_summary": forecast.hourly().summary,
                "alerts": set([Alert(severity=a.severity.title(),title=a.title,uri=a.uri) for a in forecast.alerts()])
                })
        return weather

    def geocode_location(self, location_text):
        return geocoder.google(location_text, key=self.google_api_key)

    def get_forecast(self, lat, lng):
        return forecastio.load_forecast(self.forecast_api_key, lat, lng, units='si')

    def sensible_speed(self, speed_ms):
        """Given speed in meters/second returns kilometers/hour"""
        return round(speed_ms * 3.6, 1)

    def freedom_speed(self, speed_ms):
        """Given speed in meters/second returns miles/hour"""
        return round(speed_ms * 3.6 / 1.609344, 1)

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
