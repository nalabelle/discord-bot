"""
Google Calendar Interface
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

import pyrfc3339 as rfc3339
from dateutil import tz
from dateutil.tz import tzutc
from file_secrets import secret
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

log = logging.getLogger("CalendarCog_GoogleCalendar")

DEFAULT_REMINDER_MINUTES = 15
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.readonly",
]


@dataclass(order=True)
class CalendarInfo:
    """Calendar Meta"""

    title: str
    description: str
    timezone: str

    @staticmethod
    def from_dict(item: Dict):
        log.debug(item)
        title = item.get("summary")
        description = item.get("description", None)
        timezone = item.get("timeZone", None)
        return CalendarInfo(
            title=title,
            description=description,
            timezone=timezone,
        )


@dataclass(order=True)
class CalendarEvent:
    """Calendar Events"""

    start: datetime
    end: datetime
    title: str
    description: str
    timezone: str
    reminders: List[datetime] = field(default_factory=list)

    @staticmethod
    def from_dict(item: Dict, calendar: CalendarInfo):
        tz_string = item["start"].get("timeZone", calendar.timezone)
        event_tz = tz.gettz(tz_string)
        start = CalendarEvent._get_dt_from_dict(bound="start", item=item, zone=event_tz)
        end = CalendarEvent._get_dt_from_dict(bound="end", item=item, zone=event_tz)
        title = item.get("summary")
        description = item.get("description")
        reminder_data = item.get("reminders")
        reminders = []
        now = datetime.utcnow().replace(tzinfo=tzutc())
        if reminder_data:
            log.debug(title)
            log.debug(start)
            log.debug(reminder_data)
            for override in reminder_data.get("overrides", []):
                reminder = start - timedelta(minutes=override["minutes"])
                if reminder == start and end == start + timedelta(days=1):
                    # all day events with reminder at 0 minutes -> at 9am
                    reminder = start + timedelta(hours=9)
                if reminder > now:
                    log.debug("Event Reminder: %s", reminder)
                    reminders.append(reminder)
        reminders.sort()
        return CalendarEvent(
            start=start,
            end=end,
            title=title,
            description=description,
            timezone=tz_string,
            reminders=reminders,
        )

    @staticmethod
    def _get_dt_from_dict(bound: str, item: Dict, zone: tz) -> str:
        time = None
        if "dateTime" in item[bound]:
            time = rfc3339.parse(item[bound]["dateTime"])
        else:
            time = datetime.strptime(item[bound]["date"], "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, tzinfo=zone
            )
        return time.astimezone(tzutc())


class GoogleCalendar:
    """Calendar Operations Class"""

    def __init__(self, calendar_id=None, refresh_token=None):
        self.calendar_id = calendar_id
        self._calendar_info = None
        self._calendar = None
        self._creds = None
        self.access_token = None
        self.refresh_token = refresh_token

    def events(self, time_min: datetime, time_max: datetime) -> List[CalendarEvent]:
        time_min = rfc3339.generate(time_min)
        time_max = rfc3339.generate(time_max)
        calendar_items = self._list_events(
            orderBy="startTime", timeMin=time_min, timeMax=time_max, singleEvents=True
        )["items"]
        return [CalendarEvent.from_dict(x, self.info) for x in calendar_items]

    @property
    def info(self) -> CalendarInfo:
        return self._calendar_info or self._build_calendar_info()

    def _build_calendar_info(self) -> CalendarInfo:
        self._calendar_info = CalendarInfo.from_dict(self._get_info())
        return self._calendar_info

    @property
    def calendar(self):
        return self._calendar or self._build_calendar()

    def _build_calendar(self):
        if not self.creds:
            raise RuntimeError("no credentials")
        self._calendar = build("calendar", "v3", credentials=self.creds, cache_discovery=False)
        return self._calendar

    @property
    def creds(self):
        return self._creds or self._build_creds()

    def _build_creds(self):
        if not self.refresh_token:
            raise RuntimeError("no refresh token")
        client_id = secret("google_client_id")
        client_secret = secret("google_client_secret")
        self._creds = Credentials(
            self.access_token,
            refresh_token=self.refresh_token,
            token_uri="https://accounts.google.com/o/oauth2/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        return self._creds

    def _get_info(self):
        if not self.calendar_id:
            raise RuntimeError("Need Calendar ID")
        return self.calendar.calendarList().get(calendarId=self.calendar_id).execute()

    def _list_events(self, **kwargs):
        if not self.calendar_id:
            raise RuntimeError("Need Calendar ID")
        return self.calendar.events().list(calendarId=self.calendar_id, **kwargs).execute()

    def client_config(self):
        client_id = secret("google_client_id")
        client_secret = secret("google_client_secret")
        config = {
            "installed": {
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                "client_id": client_id,
                "client_secret": client_secret,
            }
        }
        return config

    def get_auth_url(self):
        flow = InstalledAppFlow.from_client_config(self.client_config(), SCOPES)
        flow.redirect_uri = flow._OOB_REDIRECT_URI
        auth_url, _ = flow.authorization_url()
        self.flow = flow
        return auth_url

    def submit_auth_code(self, code):
        if not self.flow:
            raise RuntimeError("Not Currently In Flow")
        self.flow.fetch_token(code=code)
        self._creds = self.flow.credentials
        self.access_token = self.creds.token
        self.refresh_token = self.creds.refresh_token
        return self.refresh_token
