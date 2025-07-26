import time
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def load_credentials():
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh()
    except Exception:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_next_event(creds):
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow()
    now_str = now.isoformat() + 'Z'
    later_str = (now + timedelta(minutes=150)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_str,
        timeMax=later_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    print("#####")
    print(events)
    if events:
        e = events[0]
        summary = e.get("summary", "(Kein Titel)")
        start = e["start"].get("dateTime") or e["start"].get("date")
        end = e["end"].get("dateTime") or e["end"].get("date")
        return f"Nächstes Event: {summary} ({start} – {end})"
    else:
        return "Kein Event in den nächsten 15 Minuten."

def main():
    print("Starte Kalenderabfrage… (alle 10 Sekunden)")
    creds = load_credentials()
    while True:
        try:
            info = get_next_event(creds)
            print(f"[{datetime.now:while().strftime('%H:%M:%S')}] {info}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] FEHLER: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()

