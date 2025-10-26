"""
Tools package for AURA AI Assistant.
Each tool module contains function declarations and implementations.
"""

from .calendar_tool import get_calendar_events, calendar_declaration
from .weather_tool import get_weather, get_weather_data, weather_declaration
from .time_tool import get_time, get_date, time_declaration, date_declaration
from .search_tool import search_web, get_search_results_data, search_declaration

# Import To-Do App tools
from core.apps.todo import (
    todo_declarations,
    add_task,
    get_tasks,
    update_task,
    delete_task,
    complete_task,
    search_tasks,
    get_tasks_data
)

# Export all tool declarations for easy import
TOOL_DECLARATIONS = [
    calendar_declaration,
    weather_declaration,
    time_declaration,
    date_declaration,
    search_declaration,
    *todo_declarations  # Unpack all 6 to-do tool declarations
]

# Export all callable functions
TOOL_FUNCTIONS = {
    "get_calendar_events": get_calendar_events,
    "get_weather": get_weather,
    "get_weather_data": get_weather_data,
    "get_time": get_time,
    "get_date": get_date,
    "search_web": search_web,
    # To-Do App functions
    "add_task": add_task,
    "get_tasks": get_tasks,
    "update_task": update_task,
    "delete_task": delete_task,
    "complete_task": complete_task,
    "search_tasks": search_tasks
}

__all__ = [
    "get_calendar_events",
    "get_weather",
    "get_weather_data",
    "get_time",
    "get_date",
    "search_web",
    "get_search_results_data",
    # To-Do App exports
    "add_task",
    "get_tasks",
    "update_task",
    "delete_task",
    "complete_task",
    "search_tasks",
    "get_tasks_data",
    "TOOL_DECLARATIONS",
    "TOOL_FUNCTIONS"
]
