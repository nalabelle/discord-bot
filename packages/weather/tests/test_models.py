"""
Models Tests
"""

import pytest

from weather.models import TempRange, Wind
from weather.measurements import Bearing, Speed
import json

from cattrs import structure, unstructure

def test_temp_range():
    """Tests whether TempRange can be created"""
    temp_range = TempRange(10, 20)
    assert temp_range is not None, "TempRange can be created"

def test_temp_range_from_json():
    """Tests whether TempRange can be created from a json string"""
    json_string = '{"high": 25, "low": 28.4}'
    result = structure(json.loads(json_string), TempRange)
    assert result.high == 25.0, "We get the correct value for the TempRange high"
    assert result.low == 28.4, "We get the correct value for the TempRange low"

def test_wind():
    """Tests whether Wind can be created"""
    result = Wind(Bearing.NNW, Speed(15))
    assert result is not None, "Wind can be created"

def test_wind_from_json():
    """Tests whether Wind can be created from a json string"""
    json_string = '{"Bearing": 330.4, "speed": 2.3}'
    result = Wind(Bearing.NNW, Speed(15))
    #print(json.dumps(unstructure(result)))
    result = structure(json.loads(json_string), Wind)
    assert result.bearing == 25.0, "We get the correct value for the TempRange high"
    assert result.speed == 28.4, "We get the correct value for the TempRange low"


