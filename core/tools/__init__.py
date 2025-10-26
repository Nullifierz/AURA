"""
Tools package for AURA AI Assistant.
Each tool module contains function declarations and implementations.
"""

from .calendar_tool import get_calendar_events, calendar_declaration
from .weather_tool import get_weather, get_weather_data, weather_declaration
from .time_tool import get_time, get_date, time_declaration, date_declaration
from .search_tool import search_web, get_search_results_data, search_declaration

# Export all tool declarations for easy import
TOOL_DECLARATIONS = [
    calendar_declaration,
    weather_declaration,
    time_declaration,
    date_declaration,
    search_declaration
]

# Export all callable functions
TOOL_FUNCTIONS = {
    "get_calendar_events": get_calendar_events,
    "get_weather": get_weather,
    "get_weather_data": get_weather_data,
    "get_time": get_time,
    "get_date": get_date,
    "search_web": search_web
}

__all__ = [
    "get_calendar_events",
    "get_weather",
    "get_weather_data",
    "get_time",
    "get_date",
    "search_web",
    "get_search_results_data",
    "TOOL_DECLARATIONS",
    "TOOL_FUNCTIONS"
]
