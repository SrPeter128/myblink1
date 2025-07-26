from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta


# Wenn du nur lesenden Zugriff brauchst:
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_next_events():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    future = (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).isoformat() + 'Z'

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          timeMax=future, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

events = get_next_events()

if any(e for e in events if e['start']):
    print("Rot – gleich oder aktuell in Termin")
else:
    print("Grün – kein Termin")

now = datetime.utcnow()
red = False
yellow = False

for e in events:
    start = datetime.fromisoformat(e["start"]["dateTime"][:-1])
    end = datetime.fromisoformat(e["end"]["dateTime"][:-1])
    if start <= now <= end:
        red = True
    elif now <= start <= now + timedelta(minutes=5):
        yellow = True

if red:
    color = "red"
elif yellow:
    color = "yellow"
else:
    color = "green"

