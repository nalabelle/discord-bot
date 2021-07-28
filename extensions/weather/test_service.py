"""
Service Test
"""

import json
from unittest.mock import patch

from forecastio.models import Forecast
from geocoder.google import GoogleResult

from .service import WeatherService


@patch("file_secrets.file_secrets.FileSecrets.get")
# pylint: disable=unused-argument
def test_weather(secrets):
    weather_service = WeatherService()

    testdata = None
    response_file = open("weather/api_test_response.txt", "r")
    testdata = response_file.read()
    response_file.close()

    test_forecast = Forecast(json.loads(testdata), None, None)

    geocode_file = open("weather/api_geocode_test.txt", "r")
    testdata = geocode_file.read()
    geocode_file.close()
    test_geocode = GoogleResult(json.loads(testdata)["results"][0])

    weather = weather_service.forecast_to_object(test_geocode.address, test_forecast)
    assert weather is not None, "Weather Service Works"
