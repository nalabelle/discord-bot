from .calendar import CalendarData
from .google_calendar import GoogleCalendar

calendar = None
gcal = None


def test_setup():
    calendar = CalendarData()
    assert calendar is not None, "Calendar loads"
    gcal = GoogleCalendar()
    assert gcal is not None, "Google Calendar loads"

