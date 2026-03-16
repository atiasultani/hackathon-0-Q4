#!/usr/bin/env python3
"""
Calendar Watcher for Gold Tier AI Employee System
Monitors Google Calendar for upcoming events and creates task files
for meetings, deadlines, and reminders in Needs_Action/
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    print("Google API libraries not installed. Using mock implementation.")

BASE_PATH = Path(__file__).parent.parent
NEEDS_ACTION_DIR = BASE_PATH / "Needs_Action"
LOGS_DIR = BASE_PATH / "Logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def log_action(action_type: str, target: str, approval_status: str, result: str):
    """Create structured JSON log entry"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "action_type": action_type,
        "target": target,
        "approval_status": approval_status,
        "result": result
    }

    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    logs = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)


def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    if not HAS_GOOGLE_API:
        return None

    creds = None
    token_path = BASE_PATH / "integrations" / "gmail" / "token.json"
    credentials_path = BASE_PATH / "integrations" / "gmail" / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def create_task_from_event(event: Dict, reminder_type: str = "upcoming"):
    """Create a task file from calendar event"""
    event_id = event.get('id', 'unknown')
    summary = event.get('summary', 'Untitled Event')
    start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
    description = event.get('description', 'No description')
    attendees = event.get('attendees', [])
    location = event.get('location', '')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_summary = summary.replace(" ", "_").replace("/", "_")[:50]

    task_filename = f"CALENDAR_{reminder_type.upper()}_{sanitized_summary}_{timestamp}.md"
    task_path = NEEDS_ACTION_DIR / task_filename

    attendee_list = "\n".join([f"- {a.get('email', 'Unknown')}" for a in attendees]) if attendees else "None"

    task_content = f"""---
type: calendar_event
event_type: {reminder_type}
event_id: {event_id}
priority: {'high' if reminder_type == 'deadline' else 'normal'}
status: pending
event_time: {start}
received_at: {datetime.now().isoformat()}
---

# Calendar {reminder_type.title()}: {summary}

## Event Details
- **Time:** {start}
- **Location:** {location if location else 'Not specified'}

## Attendees
{attendee_list}

## Description
{description}

## Action Required
{'Prepare for this upcoming meeting.' if reminder_type == 'meeting' else 'Review this calendar event.'}
"""

    with open(task_path, 'w') as f:
        f.write(task_content)

    log_action("calendar_event", task_filename, "auto", "success")
    print(f"Calendar Watcher: Created task {task_filename}")


def check_upcoming_events():
    """Check for upcoming calendar events"""
    if not HAS_GOOGLE_API:
        check_upcoming_events_mock()
        return

    try:
        service = get_calendar_service()
        if not service:
            return

        now = datetime.utcnow().isoformat() + 'Z'
        end_time = (datetime.utcnow() + timedelta(hours=24)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        for event in events:
            start = event.get('start', {}).get('dateTime', '')
            if start:
                event_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_until = event_time - datetime.now(event_time.tzinfo)

                # Create reminder tasks based on time until event
                if timedelta(hours=0) < time_until <= timedelta(hours=1):
                    create_task_from_event(event, "urgent")
                elif timedelta(hours=1) < time_until <= timedelta(hours=4):
                    create_task_from_event(event, "upcoming")
                elif timedelta(hours=20) < time_until <= timedelta(hours=24):
                    create_task_from_event(event, "tomorrow")

    except Exception as e:
        print(f"Calendar Watcher Error: {e}")
        log_action("calendar_check", "calendar_watcher", "auto", f"failed: {str(e)}")


def check_upcoming_events_mock():
    """Mock implementation for testing without Google API"""
    import random

    if random.randint(1, 40) == 1:  # ~2.5% chance every check
        sample_events = [
            {
                'id': f'mock_event_{int(time.time())}',
                'summary': 'Team Standup Meeting',
                'start': {'dateTime': (datetime.now() + timedelta(hours=2)).isoformat()},
                'description': 'Daily team sync to discuss progress and blockers',
                'location': 'Zoom - Main Room',
                'attendees': [{'email': 'team@company.com'}]
            },
            {
                'id': f'mock_event_{int(time.time())}',
                'summary': 'Client Presentation',
                'start': {'dateTime': (datetime.now() + timedelta(hours=4)).isoformat()},
                'description': 'Quarterly business review with key client',
                'location': 'Conference Room A',
                'attendees': [{'email': 'client@example.com'}, {'email': 'sales@company.com'}]
            },
            {
                'id': f'mock_event_{int(time.time())}',
                'summary': 'Invoice Deadline',
                'start': {'dateTime': (datetime.now() + timedelta(hours=22)).isoformat()},
                'description': 'Deadline to submit monthly invoices',
                'location': '',
                'attendees': []
            }
        ]

        event = random.choice(sample_events)
        create_task_from_event(event, "upcoming")


def watch():
    """Main watch loop"""
    print("Calendar Watcher running...")
    log_action("watcher_start", "calendar_watcher", "auto", "started")

    while True:
        try:
            check_upcoming_events()
            time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\nCalendar Watcher stopped by user")
            log_action("watcher_stop", "calendar_watcher", "auto", "stopped")
            break
        except Exception as e:
            print(f"Error in Calendar Watcher: {e}")
            log_action("watcher_error", "calendar_watcher", "auto", f"error: {str(e)}")
            time.sleep(300)


if __name__ == "__main__":
    watch()
