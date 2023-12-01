"""
Models for representing basic weather data
"""

from __future__ import annotations

import enum

class Icon(enum.StrEnum):
    """Icon definitions"""

    CLEAR_DAY = "clear-day"
    CLEAR_NIGHT = "clear-night"
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"
    WIND = "wind"
    FOG = "fog"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY_DAY = "partly-cloudy-day"
    PARTLY_CLOUDY_NIGHT = "partly-cloudy-night"
    OTHER = "other"

    @staticmethod
    def __icon_map(value: str) -> str:
        icon_mapping = {
            "clear-day": "🌞",
            "clear-night": "🌚",
            "rain": "☔",
            "snow": "⛄",
            "sleet": "🌨",
            "wind": "🍃",
            "fog": "🌁",
            "cloudy": "☁",
            "partly_cloudy_day": "⛅",
            "partly_cloudy_night": "🌛",
            "other": "⁉",
            }
        return icon_mapping.get(value)

    def __str__(self) -> str:
        return Icon.__icon_map(self.value)


class Bearing(enum.StrEnum):
    """Stores degree to bearing mappings"""

    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE ="SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"

    @staticmethod
    def __degree_map() -> list[(int, int, Bearing)]:
        return [
            (0, 11.25, Bearing.N),
            (348.75, 360, Bearing.N),
            (11.25, 33.75, Bearing.NNE),
            (33.75, 56.25, Bearing.NE),
            (56.25, 78.75, Bearing.ENE),
            (78.75, 101.25, Bearing.E),
            (101.25, 123.75, Bearing.ESE),
            (123.75, 146.25, Bearing.SE),
            (146.25, 168.75, Bearing.SSE),
            (168.75, 191.25, Bearing.S),
            (191.25, 213.75, Bearing.SSW),
            (213.75, 236.75, Bearing.SW),
            (236.75, 258.75, Bearing.WSW),
            (258.75, 281.25, Bearing.W),
            (281.25, 303.75, Bearing.WNW),
            (303.75, 326.25, Bearing.NW),
            (326.25, 348.75, Bearing.NNW)
        ]

    @staticmethod
    def from_degree(degrees: float) -> Bearing:
        """Takes a number in degrees and returns a string bearing"""
        conversions = Bearing.__degree_map()

        for values in conversions:
            # More cardinal bearings get inclusive ranges, less cardinal get exclusive
            if len(values[2].value) > 2:
                if values[0] < degrees < values[1]:
                    return values[2]
            else:
                if values[0] <= degrees <= values[1]:
                    return values[2]
        raise ValueError(f"{degrees} is not a valid degree heading")

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

    def __str__(self) -> str:
        return self.formatted()

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

    def formatted(self) -> str:
        """Returns a formatted string containing both Celsius and Fahrenheit"""
        return f"{self.kph():,g} kph ({self.mph():,g} mph)"

    def __str__(self) -> str:
        return self.formatted()

