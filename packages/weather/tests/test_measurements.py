"""
Measurements Tests
"""

import pytest

from weather.measurements import Icon, Bearing, Temp, Speed

from cattrs import structure, unstructure

def test_icon():
    """Tests whether icons can be created"""
    result = structure("snow", Icon)
    assert f"{result}" == "⛄", "We get an Icon object with the value for snow"

def test_bearing():
    """Tests whether bearings can be created"""
    assert Bearing("NE") is not None, "We can create a Bearing by string"
    assert Bearing.from_degree(20) is Bearing.NNE, "We can create a Bearing by degree"
    result = structure("NNE", Bearing)
    assert f"{result}" == "NNE", "We can structure a Bearing from string"

def test_temp():
    """Tests whether temps can be created"""
    temp = Temp(10.101)
    assert temp is not None, "We can create a Temp from a float"
    assert f"{temp}" == "10°C (50°F)", "Temps stringify into rounded values and include F"
    result = structure("13.1", Temp)
    assert f"{result}" == "13°C (56°F)", "We can structure a Temp from string"

def test_speed():
    """Tests whether speeds can be created"""
    speed = Speed(10.101)
    assert speed is not None, "We can create a Speed from a float"
    assert f"{speed}" == "36.4 kph (22.6 mph)", "Speeds stringify into rounded values and include both kph and mph"
    result = structure("13.1", Speed)
    assert f"{result}" == "47.2 kph (29.3 mph)", "We can structure a Speed from string"

