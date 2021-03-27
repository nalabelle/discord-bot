"""
Calendar Tests
"""
import datetime
import time
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from dateutil.tz import tzutc
from libfaketime import fake_time

from .calendar import Calendar, CalendarData
from .test_google_calendar import MockGoogleCalendar

mock_cog = Mock()
mock_cog.data_path = "/dev/null"

mock_from_yaml = Mock(spec=CalendarData)
mock_from_yaml.return_value = CalendarData()

mock_tick = Mock()


@patch.object(Calendar, "tick", mock_tick)
@patch.object(CalendarData, "from_yaml", mock_from_yaml)
@fake_time("2021-03-26 00:00:01", tz_offset=0)
@pytest.mark.asyncio
class TestCalendar(unittest.TestCase):
    def test_set_next_execution(self):
        cal = Calendar(mock_cog)
        cal.set_next_execution()
        assert cal.next_execution == datetime(2021, 3, 26, 1, tzinfo=tzutc())

    def test_summary_embeds(self):
        cal = Calendar(mock_cog)
        for embed_channel_id, embed in cal.summary_embeds(1).items():
            assert embed_channel_id == 1
            assert embed == None
