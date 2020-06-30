from dateutil import tz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from services.config import Secrets
from googleapiclient.discovery import build
import pickle
import datetime
import os.path
import sys,os

SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events.readonly',
        ]

class GoogleCalendar:
    def __init__(self, calendar_id=None, refresh_token=None):
        self.creds = None
        self.service = None
        self.access_token = None

        self.calendar_id = calendar_id
        self.refresh_token = refresh_token

        if self.refresh_token:
            self.creds = self.credentials()
            self.get_service()

    def get_service(self):
        if not self.creds:
            raise Error('no credentials')
        self.calendar = build('calendar', 'v3', credentials=self.creds, cache_discovery=False)
        return self.calendar

    def get_info(self):
        if not self.calendar_id:
            raise Error("Need Calendar ID")
        return self.calendar.calendars().get(calendarId=self.calendar_id).execute()

    def list_events(self, **kwargs):
        if not self.calendar_id:
            raise Error("Need Calendar ID")
        return self.calendar.events().list(calendarId=self.calendar_id, **kwargs).execute()

    def client_config(self):
        client_id = Secrets('google_client_id')
        client_secret = Secrets('google_client_secret')
        config = {
                "installed": {
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://accounts.google.com/o/oauth2/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                        "client_id": client_id,
                        "client_secret": client_secret
                        }
                }
        return config

    def credentials(self):
        client_id = Secrets('google_client_id')
        client_secret = Secrets('google_client_secret')
        creds = Credentials(
            self.access_token,
            refresh_token=self.refresh_token,
            token_uri="https://accounts.google.com/o/oauth2/token",
            client_id=client_id,
            client_secret=client_secret
            )
        return creds

    def get_auth_url(self):
        flow = InstalledAppFlow.from_client_config(self.client_config(), SCOPES)
        flow.redirect_uri = flow._OOB_REDIRECT_URI
        auth_url, _ = flow.authorization_url()
        self.flow = flow
        return auth_url

    def submit_auth_code(self, code):
        if not self.flow:
            raise Error('Not Currently In Flow')
        self.flow.fetch_token(code=code)
        self.creds = self.flow.credentials
        self.access_token = self.creds.token
        self.refresh_token = self.creds.refresh_token
        self.get_service()
        return self.refresh_token


