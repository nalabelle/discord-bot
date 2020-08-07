from .service import WeatherService
weather_service = WeatherService()

def test_geocode():
    o = weather_service.geocode_location('90210')
    print(o)

def test_weather():
    o = weather_service.get_weather('90210')
    print(o)
    assert o is not None, "Weather Service Works"
