import subprocess
import asyncio
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Switch
from textual.containers import Container
from textual import log

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from blink1.blink1 import Blink1
from dateutil.parser import parse
from datetime import datetime, timedelta, timezone

import time

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class BlinkApp(App):
    CSS_PATH = None

    def __init__(self):
        super().__init__()
        self.automatik = True
        self.current_color = "green"
        self.creds = self.load_credentials()


    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("blink(1) Statuslicht", id="title")
        yield Container(
            Button("🟢 Grün", id="green", variant="success"),
            Button("🟡 Gelb", id="yellow", variant="warning"),
            Button("🔴 Rot", id="red", variant="error"),
        )
        #yield Static("Override:")
        #yield Switch(name="Override", value=True, id="Override_switch")
        #yield Static("OK", id="status_text")
        yield Static("Aktuelle Farbe: ⚪", id="status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        
        #if not self.automatik:
        #    return  # manuelles Umschalten deaktiviert im Automatikmodus
        self.set_color(event.button.id)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.automatik = event.value

    def set_color(self, color_id: str):
        
        b1 = Blink1()
        
        if color_id in ["red", "green", "yellow"]:
            emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(color_id, "⚪")
            b1.fade_to_color(1000, color_id)
            self.query_one("#status", Static).update(f"Aktuelle Farbe: {emoji}")
            self.current_color = color_id
        
        elif color_id == "blink_blue":
            current_color = self.current_color
            b1.play_pattern_local("3, #0261fa,0.1,1, #0a0a0a,0.1,1,  #0a0a0a,0.1,2, #0261fa,0.1,2")
            b1.fade_to_color(100, current_color)



    def load_credentials(self):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def get_upcoming_events(self):
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.utcnow().isoformat() + 'Z'
        future = (datetime.utcnow() + timedelta(minutes=15)).isoformat() + 'Z'

        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=future, singleEvents=True,
                                              orderBy='startTime').execute()
        return events_result.get('items', [])

    def determine_color_from_calendar(self, events):
        now = datetime.now(timezone.utc)
        for e in events:
            start = parse(e["start"].get("dateTime") or e["start"]["date"])
            end = parse(e["end"].get("dateTime") or e["end"]["date"])
            if start <= now <= end:
                return "red"
            elif now <= start <= now + timedelta(minutes=5):
                self.current_color = "yellow"
                return "blink_blue"
            elif now <= start <= now + timedelta(minutes=10):
                return "blink_blue"


    async def on_mount(self) -> None:
        # Starte Hintergrundtask
        self.set_interval(10, self.check_calendar)
        

    async def check_calendar(self) -> None:
        
        if not self.automatik:
            return
#        try:
        events = self.get_upcoming_events()
        color = self.determine_color_from_calendar(events)
        self.set_color(color)
#        except Exception as e:
#            self.query_one("#status_text", Static).update(e)
#            self.log(f"Kalenderfehler: {e}")

if __name__ == "__main__":
    BlinkApp().run()

