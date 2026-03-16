import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
import aiohttp
import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = FastAPI(title="Calendar MCP Server", version="1.0.0")

# Scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarAPI:
    def __init__(self):
        self.creds = None
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    async def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None

        # Token file stores the user's access and refresh tokens
        token_path = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH", "token.json")

        # Load existing credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # In a real implementation, we would use the OAuth flow
                # For this mock implementation, we'll simulate authentication
                pass

            self.creds = creds

        # Build the service object
        try:
            self.service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
            return True
        except Exception as e:
            print(f"Could not authenticate with Google Calendar: {str(e)}")
            return False

    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event"""
        # For this implementation, we'll create a mock implementation that simulates the API
        # In a real implementation, we would use the self.service.events().insert() method

        try:
            # Extract event details
            summary = event_data.get('summary', 'New Event')
            description = event_data.get('description', '')
            start_time = event_data.get('start_time')  # ISO format string
            end_time = event_data.get('end_time')  # ISO format string
            attendees = event_data.get('attendees', [])
            location = event_data.get('location', '')

            if not start_time or not end_time:
                raise Exception("Start and end times are required")

            # In a real implementation, we would create the event using the Google Calendar API
            # For this mock implementation, we'll simulate the event creation
            import random
            event_id = f"event_{random.randint(1000000000, 9999999999)}"

            # Format the event for Google Calendar API
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'attendees': [{'email': email} for email in attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            # Mock response as if the event was created
            return {
                "status": "success",
                "event_id": event_id,
                "event": {
                    "id": event_id,
                    "summary": summary,
                    "start": start_time,
                    "end": end_time,
                    "location": location,
                    "description": description,
                    "attendees": attendees
                },
                "message": f"Event '{summary}' created successfully"
            }
        except Exception as e:
            raise Exception(f"Failed to create event: {str(e)}")

    async def get_events(self, time_min: str = None, time_max: str = None, max_results: int = 10) -> Dict[str, Any]:
        """Get upcoming calendar events"""
        try:
            # In a real implementation, we would use the Google Calendar API
            # For this mock implementation, we'll return simulated events

            # Create mock events
            import random
            from datetime import datetime, timedelta

            events = []
            for i in range(min(max_results, 5)):  # Limit to 5 mock events
                start_dt = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
                end_dt = start_dt + timedelta(hours=1)

                event = {
                    "id": f"mock_event_{i}",
                    "summary": f"Mock Event {i+1}",
                    "start": {
                        "dateTime": start_dt.isoformat(),
                        "timeZone": "America/Los_Angeles"
                    },
                    "end": {
                        "dateTime": end_dt.isoformat(),
                        "timeZone": "America/Los_Angeles"
                    },
                    "location": "Virtual Meeting" if random.choice([True, False]) else f"Location {i+1}"
                }
                events.append(event)

            return {
                "status": "success",
                "events": events,
                "count": len(events),
                "message": f"Retrieved {len(events)} events"
            }
        except Exception as e:
            raise Exception(f"Failed to get events: {str(e)}")

    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a calendar event"""
        try:
            # In a real implementation, we would update the event using the Google Calendar API
            # For this mock implementation, we'll simulate the update

            summary = event_data.get('summary', f"Updated Event {event_id}")
            start_time = event_data.get('start_time')
            end_time = event_data.get('end_time')
            description = event_data.get('description', '')
            location = event_data.get('location', '')

            # Mock response as if the event was updated
            updated_event = {
                "id": event_id,
                "summary": summary,
                "start": start_time,
                "end": end_time,
                "location": location,
                "description": description
            }

            return {
                "status": "success",
                "event": updated_event,
                "message": f"Event '{event_id}' updated successfully"
            }
        except Exception as e:
            raise Exception(f"Failed to update event: {str(e)}")

    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete a calendar event"""
        try:
            # In a real implementation, we would delete the event using the Google Calendar API
            # For this mock implementation, we'll simulate the deletion

            return {
                "status": "success",
                "event_id": event_id,
                "message": f"Event '{event_id}' deleted successfully"
            }
        except Exception as e:
            raise Exception(f"Failed to delete event: {str(e)}")

    async def find_free_slots(self, date_range: Dict[str, str], duration_minutes: int = 60) -> Dict[str, Any]:
        """Find free time slots within a date range"""
        try:
            # In a real implementation, we would use the Google Calendar API's freebusy query
            # For this mock implementation, we'll simulate finding free slots

            import random
            from datetime import datetime, timedelta

            start_date_str = date_range.get('start')
            end_date_str = date_range.get('end')

            # Parse dates or use defaults
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_date = datetime.now()

            if end_date_str:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            else:
                end_date = start_date + timedelta(days=7)

            # Generate some mock free slots
            free_slots = []
            current_date = start_date

            while current_date < end_date:
                # Randomly decide if this day has free slots (70% chance)
                if random.random() > 0.3:
                    # Add 1-3 free slots for this day
                    for _ in range(random.randint(1, 3)):
                        hour = random.randint(9, 17)  # Between 9 AM and 5 PM
                        minute = random.choice([0, 15, 30, 45])

                        slot_start = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        slot_end = slot_start + timedelta(minutes=duration_minutes)

                        free_slots.append({
                            "start": slot_start.isoformat(),
                            "end": slot_end.isoformat()
                        })

                current_date += timedelta(days=1)

            # Sort slots by start time
            free_slots.sort(key=lambda x: x['start'])

            return {
                "status": "success",
                "free_slots": free_slots,
                "count": len(free_slots),
                "message": f"Found {len(free_slots)} free time slots"
            }
        except Exception as e:
            raise Exception(f"Failed to find free slots: {str(e)}")

calendar_api = CalendarAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to authenticate (this would connect to the actual API in a real implementation)
        authenticated = await calendar_api.authenticate()
        return {
            "status": "healthy",
            "authenticated": authenticated,
            "calendar_id": calendar_api.calendar_id
        }
    except Exception as e:
        return {
            "status": "healthy",  # Still return healthy since it's a mock implementation
            "authenticated": False,
            "error": str(e),
            "message": "Service running but authentication failed - check credentials"
        }

@app.post("/create_event")
async def create_calendar_event(event_data: Dict[str, Any]):
    """Create a calendar event"""
    try:
        result = await calendar_api.create_event(event_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/get_events")
async def get_calendar_events(time_min: str = None, time_max: str = None, max_results: int = 10):
    """Get upcoming calendar events"""
    try:
        result = await calendar_api.get_events(time_min, time_max, max_results)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@app.put("/update_event/{event_id}")
async def update_calendar_event(event_id: str, event_data: Dict[str, Any]):
    """Update a calendar event"""
    try:
        result = await calendar_api.update_event(event_id, event_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@app.delete("/delete_event/{event_id}")
async def delete_calendar_event(event_id: str):
    """Delete a calendar event"""
    try:
        result = await calendar_api.delete_event(event_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

@app.post("/find_free_slots")
async def find_free_time_slots(date_range: Dict[str, str], duration_minutes: int = 60):
    """Find free time slots within a date range"""
    try:
        result = await calendar_api.find_free_slots(date_range, duration_minutes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find free slots: {str(e)}")

@app.post("/schedule_meeting")
async def schedule_meeting(meeting_data: Dict[str, Any]):
    """
    Schedule a meeting with automatic time slot finding and calendar creation
    Expected format:
    {
        "summary": "Meeting title",
        "description": "Meeting description",
        "attendees": ["email1@example.com", "email2@example.com"],
        "duration_minutes": 60,
        "preferred_dates": {
            "start": "2023-12-01T00:00:00Z",
            "end": "2023-12-07T23:59:59Z"
        },
        "location": "Virtual Meeting Room"
    }
    """
    try:
        # First, find free slots based on preferences
        date_range = meeting_data.get('preferred_dates', {})
        duration_minutes = meeting_data.get('duration_minutes', 60)

        free_slots_result = await calendar_api.find_free_slots(date_range, duration_minutes)
        free_slots = free_slots_result.get('free_slots', [])

        if not free_slots:
            return {
                "status": "no_availability",
                "message": "No free time slots available for the requested dates",
                "suggestion": "Try extending the date range or adjusting the duration"
            }

        # Take the first available slot
        selected_slot = free_slots[0]

        # Create the event
        event_data = {
            'summary': meeting_data.get('summary', 'Scheduled Meeting'),
            'description': meeting_data.get('description', ''),
            'start_time': selected_slot['start'],
            'end_time': selected_slot['end'],
            'attendees': meeting_data.get('attendees', []),
            'location': meeting_data.get('location', 'Virtual Meeting')
        }

        event_result = await calendar_api.create_event(event_data)

        return {
            "status": "success",
            "event": event_result.get('event'),
            "scheduled_time": selected_slot,
            "message": f"Meeting scheduled for {selected_slot['start']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule meeting: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)