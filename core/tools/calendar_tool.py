"""
Google Calendar tool for AURA AI Assistant.
Provides access to user's Google Calendar events.
"""

import os
import pytz
from datetime import datetime

# Google Calendar API configuration
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings", "credentials.json")

# Function declaration for Gemini API (following Google's schema)
calendar_declaration = {
    "name": "get_calendar_events",
    "description": "Retrieves upcoming events from the user's Google Calendar in Indonesia timezone (WIB). Use this when the user asks about their schedule, appointments, meetings, or upcoming events. IMPORTANT: If user asks for 'next event', 'closest schedule', 'what's next', use max_results=1. If user asks for 'today's schedule', 'all events', use max_results=5-10.",
    "parameters": {
        "type": "object",
        "properties": {
            "max_results": {
                "type": "integer",
                "description": "Maximum number of events to retrieve. Use 1 for 'next/closest event', 3-5 for 'today', 10+ for 'this week' or 'all events'. Default is 5.",
            }
        },
        "required": []
    }
}

def _get_calendar_service():
    """Create and return service object for interacting with Google Calendar API.
    
    Note: Imports are kept inside the function to avoid exposing complex library 
    functions to Gemini's function introspection, which can cause parsing errors.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, CALENDAR_SCOPES)
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        raise Exception(f"Failed to initialize calendar service: {str(e)}")

def get_calendar_events(max_results: int = 5) -> str:
    """Get upcoming events from Google Calendar in Indonesia timezone.
    
    Args:
        max_results: Maximum number of events to retrieve (default: 5)
        
    Returns:
        A formatted string containing upcoming calendar events in Indonesia time (WIB)
    """
    try:
        service = _get_calendar_service()
        
        # Use Indonesia timezone (WIB - Western Indonesia Time)
        wib = pytz.timezone('Asia/Jakarta')
        now = datetime.now(wib).isoformat()
        
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        if not events:
            return "No upcoming events found in your calendar."
        
        # Format output for easy reading
        output = "Upcoming Events:\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_title = event.get('summary', 'Untitled Event')
            
            # Remove emoji and special characters from event title
            event_title = ''.join(char for char in event_title if ord(char) < 0x10000 and not (0xD800 <= ord(char) <= 0xDFFF))
            event_title = event_title.encode('ascii', errors='ignore').decode('ascii').strip()
            
            # Format datetime for display in Indonesia timezone
            if "T" in start:  # dateTime format
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                # Convert to Indonesia timezone
                start_wib = start_dt.astimezone(wib)
                start_str = start_wib.strftime("%A, %B %d, %Y at %I:%M %p WIB")
            else:  # date format (all-day event)
                start_dt = datetime.fromisoformat(start)
                start_str = start_dt.strftime("%A, %B %d, %Y (All day)")
            
            output += f"{start_str}, {event_title}\n"
        
        return output
    except FileNotFoundError:
        return "Google Calendar credentials not found. Please set up credentials.json in the settings folder."
    except ImportError as e:
        return f"Missing required library: {str(e)}. Please run: pip install -r requirements.txt"
    except Exception as e:
        return f"Error accessing Google Calendar: {str(e)}"

def get_calendar_events_data(max_results: int = 5) -> dict:
    """Get structured calendar events data for HUD display.
    
    This is an internal function used by the backend for HUD display.
    Not exposed as a tool to Gemini.
    
    Args:
        max_results: Maximum number of events to retrieve (default: 5)
        
    Returns:
        A dictionary containing structured calendar events data
    """
    try:
        service = _get_calendar_service()
        
        # Use Indonesia timezone (WIB - Western Indonesia Time)
        wib = pytz.timezone('Asia/Jakarta')
        now = datetime.now(wib).isoformat()
        
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        if not events:
            return {
                "error": "No events",
                "message": "No upcoming events found in your calendar."
            }
        
        # Format events for table display
        events_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_title = event.get('summary', 'Untitled Event')
            event_description = event.get('description', '')
            
            # Format datetime for display in Indonesia timezone
            if "T" in start:  # dateTime format
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                # Convert to Indonesia timezone
                start_wib = start_dt.astimezone(wib)
                date_str = start_wib.strftime("%A, %B %d, %Y")
                time_str = start_wib.strftime("%I:%M %p WIB")
                is_all_day = False
            else:  # date format (all-day event)
                start_dt = datetime.fromisoformat(start)
                date_str = start_dt.strftime("%A, %B %d, %Y")
                time_str = "All Day"
                is_all_day = True
            
            events_list.append({
                "date": date_str,
                "time": time_str,
                "event": event_title,
                "description": event_description,
                "is_all_day": is_all_day
            })
        
        return {
            "events": events_list,
            "count": len(events_list)
        }
    except Exception as e:
        return {
            "error": "Error",
            "message": f"Error accessing Google Calendar: {str(e)}"
        }
