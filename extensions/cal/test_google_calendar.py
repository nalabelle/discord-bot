"""
Calendar Tests
"""
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from .google_calendar import GoogleCalendar

# Mocks as per:
# https://developers.example.com/resources/api-libraries/documentation/calendar/v3/python/latest/
MOCK_CALENDAR = {
    "kind": "calendar#calendarListEntry",
    "etag": '"1000000000000000"',
    "id": "a0000000000000000000000000@group.calendar.example.com",
    "summary": "Mock Calendar",
    "description": "Mock Calendar description",  # optional
    "timeZone": "America/Los_Angeles",
    "colorId": "15",
    "backgroundColor": "#9fc6e7",
    "foregroundColor": "#000000",
    "selected": True,
    "accessRole": "owner",
    "defaultReminders": [],
    "conferenceProperties": {"allowedConferenceSolutionTypes": ["hangoutsMeet"]},
}

MOCK_EVENTS = [
    {
        "kind": "calendar#event",
        "etag": '"1000000000000000"',
        "id": "10000000000000000000000000_20210403T010000Z",
        "status": "confirmed",
        "htmlLink": "https://www.example.com/calendar/event?eid=EVENTID1",
        "created": "2021-02-20T05:09:43.000Z",
        "updated": "2021-03-04T20:53:09.925Z",
        "summary": "DnD",
        "creator": {"email": "user1@example.com"},
        "organizer": {
            "email": "a0000000000000000000000000@group.calendar.example.com",
            "displayName": "Mock Calendar",
            "self": True,
        },
        "start": {
            "dateTime": "2021-04-02T18:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "end": {"dateTime": "2021-04-02T21:00:00-07:00", "timeZone": "America/Los_Angeles"},
        "recurringEventId": "10000000000000000000000000",
        "originalStartTime": {
            "dateTime": "2021-04-02T18:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "sequence": 2,
        "reminders": {"useDefault": True},
        "eventType": "default",
    },
    {
        "kind": "calendar#event",
        "etag": '"2000000000000000"',
        "id": "20000000000000000000000000_20210327",
        "status": "confirmed",
        "htmlLink": "https://www.example.com/calendar/event?eid=EVENTID2",
        "created": "2021-03-27T04:06:20.000Z",
        "updated": "2021-03-27T04:06:20.500Z",
        "summary": "Downtime Events Due",
        "description": "https://example.com/link",
        "creator": {"email": "user2@example.com"},
        "organizer": {
            "email": "b0000000000000000000000000@group.calendar.example.com",
            "displayName": "Example D&D",
            "self": True,
        },
        "start": {"date": "2021-03-27"},
        "end": {"date": "2021-03-28"},
        "recurringEventId": "20000000000000000000000000",
        "originalStartTime": {"date": "2021-03-27"},
        "transparency": "transparent",
        "sequence": 0,
        "guestsCanModify": True,
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 0}]},
        "eventType": "default",
    },
    {
        "kind": "calendar#event",
        "etag": '"3000000000000000"',
        "id": "30000000000000000000000000_20210403T010000Z",
        "status": "confirmed",
        "htmlLink": "https://www.example.com/calendar/event?eid=EVENTID3",
        "created": "2021-03-21T23:24:49.000Z",
        "updated": "2021-03-22T02:17:14.134Z",
        "summary": "D&D Session",
        "creator": {"email": "user2@example.com"},
        "organizer": {
            "email": "b0000000000000000000000000@group.calendar.example.com",
            "displayName": "Example D&D",
            "self": True,
        },
        "start": {"dateTime": "2021-04-02T18:00:00-07:00", "timeZone": "America/Los_Angeles"},
        "end": {"dateTime": "2021-04-02T21:00:00-07:00", "timeZone": "America/Los_Angeles"},
        "recurringEventid": "30000000000000000000000000_R20210403T010000",
        "originalStartTime": {
            "dateTime": "2021-04-02T18:00:00-07:00",
            "timeZone": "America/Los_Angeles",
        },
        "sequence": 0,
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 1440},
                {"method": "popup", "minutes": 15},
            ],
        },
        "eventType": "default",
    },
]


def MockGoogleCalendar():
    gcal = GoogleCalendar()
    gcal._list_events = MagicMock(return_value={"items": MOCK_EVENTS})
    gcal._get_info = MagicMock(return_value=MOCK_CALENDAR)
    return gcal


class TestGoogleCalendar(unittest.TestCase):
    def test_calendar_load(self):
        gcal = MockGoogleCalendar()
        assert gcal is not None, "Google Calendar loads"
        events = gcal.events(
            time_min=datetime.now(timezone.utc), time_max=datetime.now(timezone.utc)
        )
        assert len(events) == 3
