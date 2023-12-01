"""
Service Test
"""

import json
from importlib import resources as res
from unittest.mock import patch
import pytest

#from forecastio.models import Forecast
from geocoder.google import GoogleResult

#from weather.models import WeatherData
#from weather.models import Icon, Bearing, Temp, Speed

from cattrs import structure, unstructure

#@patch("file_secrets.file_secrets.FileSecrets.get")
#def test_weather(secrets):
#    """Tests weather loading"""
#
#    testdata = None
#    files = res.files("extensions.weather")
#    with files.joinpath('api_test_response.txt').open(mode='r', encoding='utf-8') as response_file:
#        testdata = response_file.read()
#        test_forecast = Forecast(json.loads(testdata), None, None)
#
#    with files.joinpath('api_geocode_test.txt').open(mode='r', encoding='utf-8') as geocode_file:
#        testdata = geocode_file.read()
#        test_geocode = GoogleResult(json.loads(testdata)["results"][0])
#
#    weather = WeatherData.from_forecast(test_geocode.address, test_forecast)
#    assert weather is not None, "Weather Service Works"
