"""
Models for representing weather data
"""

from __future__ import annotations

import datetime

from dateutil import tz
from forecastio.models import Forecast
from pydantic import BaseModel


class Icon(str):
    """Icon definitions"""

    icons = {
        "clear-day": "🌞",
        "clear-night": "🌚",
        "rain": "☔",
        "snow": "⛄",
        "sleet": "🌨",
        "wind": "🍃",
        "fog": "🌁",
        "cloudy": "☁",
        "partly-cloudy-day": "⛅",
        "partly-cloudy-night": "🌛",
        "OTHER": "⁉",
    }

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """Validates input, for pydantic"""
        if isinstance(val, str):
            icon = cls.icons[val]
            if icon:
                return cls(icon)
        raise ValueError(f"{val} is not a valid icon description")


class Bearing(str):
    """Stores degree to bearing mappings"""

    valid_bearings = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]

    @staticmethod
    # pylint: disable=too-many-return-statements,too-many-branches
    def bearing(degrees: float) -> str:
        """Takes a number in degrees and returns a string bearing"""
        if degrees >= 348.75 or degrees <= 11.25:
            return "N"
        if 11.25 < degrees < 33.75:
            return "NNE"
        if 33.75 <= degrees <= 56.25:
            return "NE"
        if 56.25 < degrees < 78.75:
            return "ENE"
        if 78.75 <= degrees <= 101.25:
            return "E"
        if 101.25 < degrees < 123.75:
            return "ESE"
        if 123.75 <= degrees <= 146.25:
            return "SE"
        if 146.25 < degrees < 168.75:
            return "SSE"
        if 168.75 <= degrees <= 191.25:
            return "S"
        if 191.25 < degrees < 213.75:
            return "SSW"
        if 213.75 <= degrees <= 236.75:
            return "SW"
        if 236.75 < degrees < 258.75:
            return "WSW"
        if 258.75 <= degrees <= 281.25:
            return "W"
        if 281.25 < degrees < 303.75:
            return "WNW"
        if 303.75 <= degrees <= 326.25:
            return "NW"
        if 326.25 < degrees < 348.75:
            return "NNW"
        raise ValueError(f"{degrees} is not a valid degree heading")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """Validates input, for pydantic"""
        if isinstance(val, str):
            if val in cls.valid_bearings:
                return cls(val)
            raise ValueError(f"{val} is not a valid bearing")
        if isinstance(val, (float, int)):
            return cls.bearing(float(val))
        raise ValueError(f"{val} is not a valid bearing or degree heading")


class Temp(float):
    """
    Temperature class with conversion

    Expects temperature in degrees Celsius
    """

    def celsius(self) -> float:
        """Returns a rounded representation of the temperature in Celsius"""
        return round(self, 0)

    def fahrenheit(self) -> float:
        """Returns a rounded representation of the temperature in Fahrenheit"""
        return round(self * 9 / 5 + 32, 0)

    def formatted(self) -> str:
        """Returns a formatted string containing both Celsius and Fahrenheit"""
        return f"{self.celsius():,g}°C ({self.fahrenheit():,g}°F)"

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """Validates input, for pydantic"""
        if isinstance(val, float):
            return cls(float(val))
        raise ValueError(f"{val} is not a valid temperature")


class Speed(float):
    """
    Speed with conversion

    Expects speed in meters/second
    """

    def kph(self) -> float:
        """Returns kilometers/hour"""
        return round(self * 3.6, 1)

    def mph(self) -> float:
        """Returns miles/hour"""
        return round(self * 3.6 / 1.609344, 1)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """Validates input, for pydantic"""
        if isinstance(val, float):
            return cls(val)
        raise ValueError(f"{val} is not a valid speed")


class TempRange(BaseModel):
    """Temperature Range Data Container"""

    high: Temp
    low: Temp


class Wind(BaseModel):
    """Wind Speed and Bearing Data Point"""

    bearing: Bearing
    speed: Speed


class Alert(BaseModel):
    """Severe Weather Alert"""

    severity: str
    title: str
    uri: str

    def __hash__(self):
        return hash((self.title, self.severity, self.uri))


class Time(BaseModel):
    """Time in native and UTC timezones, with formatters"""

    time: datetime.datetime
    local_timezone: str

    def utc_formatted(self) -> str:
        """Returns a string of the UTC representation of the time"""
        return self.time.strftime("%Y-%m-%d %H:%M UTC")

    def local_time_formatted(self) -> str:
        """Returns a string of the local representation of the time"""
        localtime = self.time.astimezone(tz=tz.gettz(self.local_timezone))
        return localtime.strftime(f"%Y-%m-%d %H:%M {self.local_timezone}")


class WeatherData(BaseModel):
    """Main Weather Data container"""

    alerts: set[Alert] = []
    current_icon: Icon
    current_summary: str
    current_temp: Temp
    daily_summary: str
    daily_temp: TempRange
    feels_like: Temp
    hourly_summary: str
    humidity: int
    location: str
    precip: int
    time: Time
    wind: Wind

    @classmethod
    def from_forecast(cls, location: str, forecast: Forecast):
        """Builds a WeatherData object, given a location string and a Forecast"""
        cur = forecast.currently()
        day = forecast.daily().data[0]

        weather = WeatherData.parse_obj(
            {
                "location": location,
                "time": {"time": cur.time, "local_timezone": forecast.json["timezone"]},
                "current_summary": cur.summary,
                "hourly_summary": forecast.minutely().summary,
                "daily_summary": forecast.hourly().summary,
                "current_icon": cur.icon,
                "current_temp": cur.temperature,
                "feels_like": cur.apparentTemperature,
                "daily_temp": {
                    "high": day.temperatureHigh,
                    "low": day.temperatureLow,
                },
                "humidity": round(cur.humidity * 100, 0),
                "precip": round(cur.precipProbability * 100, 0),
                "wind": {
                    "bearing": cur.windBearing,
                    "speed": cur.windSpeed,
                },
                "alerts": [
                    {"severity": a.severity.title(), "title": a.title, "uri": a.uri}
                    for a in forecast.alerts()
                ],
            }
        )
        return weather
