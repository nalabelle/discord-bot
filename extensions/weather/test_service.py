import json
from unittest.mock import patch
from .service import WeatherService, Alert
from forecastio.models import Forecast
from geocoder.google import GoogleResult

@patch('file_secrets.file_secrets.FileSecrets.get')
def test_weather(Secrets):
    weather_service = WeatherService()

    testdata = None
    f = open("weather/api_test_response.txt", "r")
    testdata = f.read()
    f.close()

    test_forecast = Forecast(json.loads(testdata), None, None)

    f = open("weather/api_geocode_test.txt", "r")
    testdata = f.read()
    test_geocode = GoogleResult(json.loads(testdata)["results"][0])

    weather = weather_service.forecast_to_object(test_geocode.address, test_forecast)
    assert weather is not None, "Weather Service Works"

