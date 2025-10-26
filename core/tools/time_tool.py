"""
Time and date tool for AURA AI Assistant.
Provides current time and date in Indonesia timezone (WIB).
"""

import pytz
from datetime import datetime

# Function declarations for Gemini API (following Google's schema)
time_declaration = {
    "name": "get_time",
    "description": "Gets the current time in Indonesia timezone (WIB - Western Indonesia Time) in 12-hour format with AM/PM. Use this when user asks 'what time is it', 'current time', or any time-related queries.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

date_declaration = {
    "name": "get_date",
    "description": "Gets the current date in Indonesia timezone (WIB) with full day name and month. Format: 'Day, Month DD, YYYY'. Use this when user asks 'what's the date', 'today's date', or any date-related queries.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
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
    """Get the current date in Indonesia timezone (WIB).

    Returns:
        A string representing the current date (e.g., "Friday, October 25, 2025")
    """
    try:
        wib = pytz.timezone('Asia/Jakarta')
        today = datetime.now(wib)
        return today.strftime("%A, %B %d, %Y")
    except Exception as e:
        # Fallback to system time if timezone fails
        today = datetime.now()
        return today.strftime("%A, %B %d, %Y")
