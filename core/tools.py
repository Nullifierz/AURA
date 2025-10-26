import os
import pytz
import requests
from datetime import datetime

# Google Calendar API configuration
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings", "credentials.json")

def _get_calendar_service():
    """Create and return service object for interacting with Google Calendar API."""
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
        A formatted string containing upcoming calendar events in Indonesia time
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
            
            # Format datetime for display in Indonesia timezone
            if "T" in start:  # dateTime format
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                # Convert to Indonesia timezone
                start_wib = start_dt.astimezone(wib)
                start_str = start_wib.strftime("%A, %B %d, %Y at %I:%M %p WIB")
            else:  # date format (all-day event)
                start_dt = datetime.fromisoformat(start)
                start_str = start_dt.strftime("%A, %B %d, %Y (All day)")
            
            output += f"- {start_str}: {event_title}\n"
        
        return output
    except FileNotFoundError:
        return "Google Calendar credentials not found. Please set up credentials.json in the settings folder."
    except ImportError as e:
        return f"Missing required library: {str(e)}. Please run: pip install -r requirements.txt"
    except Exception as e:
        return f"Error accessing Google Calendar: {str(e)}"

def get_weather(location: str, temperature: str = "C") -> str:
    """Get the current weather for a location using OpenWeatherMap API.
    
    Args:
        location: The city or location to get weather for
        temperature: The temperature unit (default: "C" for Celsius)
        
    Returns:
        A string describing the weather
    """
    try:
        from settings.config_loader import config
        
        api_key = config.get('api_keys.openweather')
        if not api_key or 'YOUR_' in api_key:
            return f"Weather API not configured. Please add your OpenWeatherMap API key to config.yaml"
        
        # OpenWeatherMap API endpoint
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Set units based on temperature preference
        units = "metric" if temperature.upper() == "C" else "imperial"
        
        params = {
            'q': location,
            'appid': api_key,
            'units': units
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            
            temp_unit = "°C" if units == "metric" else "°F"
            wind_unit = "m/s" if units == "metric" else "mph"
            
            weather_info = (
                f"The weather in {location} is {description}. "
                f"Temperature: {temp}{temp_unit} (feels like {feels_like}{temp_unit}). "
                f"Humidity: {humidity}%. Wind speed: {wind_speed} {wind_unit}."
            )
            
            return weather_info
        elif response.status_code == 404:
            return f"Location '{location}' not found. Please check the city name."
        else:
            return f"Unable to fetch weather data. Error code: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Weather service timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to weather service: {str(e)}"
    except Exception as e:
        return f"Error getting weather: {str(e)}"

def get_weather_data(location: str = "Jakarta") -> dict:
    """Get detailed weather data for HUD display using OpenWeatherMap API.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        A dictionary containing weather data for HUD display
    """
    try:
        from settings.config_loader import config
        
        api_key = config.get('api_keys.openweather')
        if not api_key or 'YOUR_' in api_key:
            return {
                "error": "Weather API not configured",
                "message": "Please add your OpenWeatherMap API key to config.yaml"
            }
        
        # OpenWeatherMap API endpoint
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'  # Use Celsius
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "location": data['name'],
                "country": data['sys']['country'],
                "temperature": round(data['main']['temp'], 1),
                "feels_like": round(data['main']['feels_like'], 1),
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "description": data['weather'][0]['description'].title(),
                "icon": data['weather'][0]['icon'],
                "wind_speed": round(data['wind']['speed'], 1),
                "clouds": data['clouds']['all'],
                "visibility": data.get('visibility', 0) / 1000,  # Convert to km
                "sunrise": datetime.fromtimestamp(data['sys']['sunrise'], tz=pytz.timezone('Asia/Jakarta')).strftime("%I:%M %p"),
                "sunset": datetime.fromtimestamp(data['sys']['sunset'], tz=pytz.timezone('Asia/Jakarta')).strftime("%I:%M %p")
            }
        elif response.status_code == 404:
            return {
                "error": "Location not found",
                "message": f"Location '{location}' not found. Please check the city name."
            }
        else:
            return {
                "error": "API error",
                "message": f"Unable to fetch weather data. Error code: {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        return {
            "error": "Timeout",
            "message": "Weather service timed out. Please try again."
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": "Connection error",
            "message": f"Error connecting to weather service: {str(e)}"
        }
    except Exception as e:
        return {
            "error": "Unknown error",
            "message": f"Error getting weather: {str(e)}"
        }

def get_time() -> str:
    """Get the current time in Indonesia timezone (WIB) in 12-hour format.

    Returns:
        A string representing the current time in Indonesia (e.g., "3:45 PM WIB")
    """
    try:
        wib = pytz.timezone('Asia/Jakarta')
        now = datetime.now(wib)
        return now.strftime("%I:%M %p").lstrip("0") + " WIB"
    except Exception as e:
        # Fallback to system time if timezone fails
        now = datetime.now()
        return now.strftime("%I:%M %p").lstrip("0")

def get_date() -> str:
    """Get the current date in Indonesia timezone.

    Returns:
        A string representing the current date (e.g., "Friday, October 24, 2025")
    """
    try:
        wib = pytz.timezone('Asia/Jakarta')
        today = datetime.now(wib)
        return today.strftime("%A, %B %d, %Y")
    except Exception as e:
        # Fallback to system time if timezone fails
        today = datetime.now()
        return today.strftime("%A, %B %d, %Y")