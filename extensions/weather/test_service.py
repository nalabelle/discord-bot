"""
Service Test
"""

import json
from importlib import resources as res
from unittest.mock import patch

from forecastio.models import Forecast
from geocoder.google import GoogleResult

from extensions.weather.models import WeatherData


@patch("file_secrets.file_secrets.FileSecrets.get")
# pylint: disable=unused-argument
def test_weather(secrets):
    """Tests weather loading"""

    testdata = None
    with res.open_text(
        "extensions.weather", "api_test_response.txt", encoding="utf-8"
    ) as response_file:
        testdata = response_file.read()
        test_forecast = Forecast(json.loads(testdata), None, None)

    with res.open_text(
        "extensions.weather", "api_geocode_test.txt", encoding="utf-8"
    ) as geocode_file:
        testdata = geocode_file.read()
        test_geocode = GoogleResult(json.loads(testdata)["results"][0])

    weather = WeatherData.from_forecast(test_geocode.address, test_forecast)
    assert weather is not None, "Weather Service Works"
