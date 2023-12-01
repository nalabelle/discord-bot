"""
Models for representing weather structures
"""

from __future__ import annotations
from attr import define

from weather.measurements import Temp, Bearing, Speed

@define
class TempRange:
    """Temperature Ranges"""

    high: Temp
    low: Temp


@define
class Wind:
    """Wind Speed and Bearing Data Point"""

    bearing: Bearing
    speed: Speed
#
#
#class Alert(BaseModel):
#    """Severe Weather Alert"""
#
#    severity: str
#    title: str
#    uri: str
#
#    def __hash__(self):
#        return hash((self.title, self.severity, self.uri))
#
#
#class Time(BaseModel):
#    """Time in native and UTC timezones, with formatters"""
#
#    time: datetime.datetime
#    local_timezone: str
#
#    def utc_formatted(self) -> str:
#        """Returns a string of the UTC representation of the time"""
#        return self.time.strftime("%Y-%m-%d %H:%M UTC")
#
#    def local_time_formatted(self) -> str:
#        """Returns a string of the local representation of the time"""
#        localtime = self.time.astimezone(tz=tz.gettz(self.local_timezone))
#        return localtime.strftime(f"%Y-%m-%d %H:%M {self.local_timezone}")
#
#
#class WeatherData(BaseModel):
#    """Main Weather Data container"""
#
#    alerts: set[Alert] = []
#    current_icon: Icon
#    current_summary: str
#    current_temp: Temp
#    daily_summary: str
#    daily_temp: TempRange
#    feels_like: Temp
#    hourly_summary: str
#    humidity: int
#    location: str
#    precip: int
#    time: Time
#    wind: Wind
#
#    @classmethod
#    def from_forecast(cls, location: str, forecast: Forecast):
#        """Builds a WeatherData object, given a location string and a Forecast"""
#        cur = forecast.currently()
#        day = forecast.daily().data[0]
#
#        weather = WeatherData.model_validate(
#            {
#                "location": location,
#                "time": {"time": cur.time, "local_timezone": forecast.json["timezone"]},
#                "current_summary": cur.summary,
#                "hourly_summary": forecast.minutely().summary,
#                "daily_summary": forecast.hourly().summary,
#                "current_icon": cur.icon.upper().replace("-","_"),
#                "current_temp": cur.temperature,
#                "feels_like": cur.apparentTemperature,
#                "daily_temp": {
#                    "high": day.temperatureHigh,
#                    "low": day.temperatureLow,
#                },
#                "humidity": round(cur.humidity * 100, 0),
#                "precip": round(cur.precipProbability * 100, 0),
#                "wind": {
#                    "bearing": cur.windBearing,
#                    "speed": cur.windSpeed,
#                },
#                "alerts": [
#                    {"severity": a.severity.title(), "title": a.title, "uri": a.uri}
#                    for a in forecast.alerts()
#                ],
#            }
#        )
#        return weather
