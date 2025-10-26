"""
Weather tool for AURA AI Assistant.
Provides real-time weather data using OpenWeatherMap API.
"""

import pytz
import requests
from datetime import datetime

# Function declaration for Gemini API (following Google's schema)
weather_declaration = {
    "name": "get_weather",
    "description": "Gets the current weather conditions for a specified location using OpenWeatherMap API. Returns temperature, feels like, humidity, wind speed, and weather description. Use this when user asks about weather, temperature, or climate conditions.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name or location to get weather for. Can be 'City' or 'City,CountryCode'. Examples: 'Jakarta', 'London,UK', 'New York,US'",
            },
            "temperature": {
                "type": "string",
                "description": "Temperature unit preference. Use 'C' for Celsius (metric) or 'F' for Fahrenheit (imperial).",
                "enum": ["C", "F"]
            }
        },
        "required": ["location"]
    }
}

def get_weather(location: str, temperature: str = "C") -> str:
    """Get the current weather for a location using OpenWeatherMap API.
    
    Args:
        location: The city or location to get weather for
        temperature: The temperature unit (default: "C" for Celsius)
        
    Returns:
        A string describing the weather conditions
    """
    try:
        from settings.config_loader import config
        
        api_key = config.get('api_keys.openweather')
        if not api_key or 'YOUR_' in api_key:
            return "Weather API not configured. Please add your OpenWeatherMap API key to config.yaml"
        
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
            
            # Use full unit names for better TTS pronunciation
            temp_unit = "degrees Celsius" if units == "metric" else "degrees Fahrenheit"
            wind_unit = "meters per second" if units == "metric" else "miles per hour"
            
            weather_info = (
                f"The weather in {location} is {description}. "
                f"Temperature: {temp} {temp_unit} (feels like {feels_like} {temp_unit}). "
                f"Humidity: {humidity} percent. Wind speed: {wind_speed} {wind_unit}."
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
    
    This is an internal function used by the backend for HUD display.
    Not exposed as a tool to Gemini.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        A dictionary containing detailed weather data for HUD display
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
