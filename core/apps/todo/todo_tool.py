"""
AI Tool declarations and functions for To-Do App
Integrates task management with AURA's AI capabilities
"""

from datetime import datetime, timedelta
from typing import Optional, List
from .todo_app import TodoApp
import re


# Initialize the To-Do app
_todo_app = TodoApp()


# ===== TOOL DECLARATIONS FOR GEMINI API =====

add_task_declaration = {
    "name": "add_task",
    "description": "Add a new task to the to-do list. Use this when user wants to create a task, add something to their to-do list, or remember to do something. Supports natural language for dates (e.g., 'tomorrow', 'next Friday', 'in 3 days').",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The task title or description. Keep it concise but descriptive."
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description or notes about the task."
            },
            "priority": {
                "type": "string",
                "description": "Task priority level.",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "Due date in natural language (e.g., 'tomorrow', 'next Monday', '2025-10-30') or ISO format."
            },
            "category": {
                "type": "string",
                "description": "Task category (e.g., 'work', 'personal', 'shopping', 'health')."
            }
        },
        "required": ["title"]
    }
}

get_tasks_declaration = {
    "name": "get_tasks",
    "description": "Get tasks from the to-do list with optional filters. Use this when user asks to see their tasks, check their to-do list, or query specific tasks. Returns structured data for display.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by task status.",
                "enum": ["pending", "in_progress", "completed"]
            },
            "priority": {
                "type": "string",
                "description": "Filter by priority level.",
                "enum": ["low", "medium", "high"]
            },
            "category": {
                "type": "string",
                "description": "Filter by category (e.g., 'work', 'personal')."
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tasks to return. Use 5 for 'show me a few tasks', 10 for normal queries, 20+ for 'show me all tasks'."
            }
        },
        "required": []
    }
}

update_task_declaration = {
    "name": "update_task",
    "description": "Update an existing task's details. Use this when user wants to modify a task, change priority, reschedule, or update task information. Requires task identification (title or recent context).",
    "parameters": {
        "type": "object",
        "properties": {
            "task_identifier": {
                "type": "string",
                "description": "Task title or unique identifier to find the task. Use the exact title from conversation context or partial match."
            },
            "title": {
                "type": "string",
                "description": "New task title."
            },
            "description": {
                "type": "string",
                "description": "New task description."
            },
            "status": {
                "type": "string",
                "description": "New task status.",
                "enum": ["pending", "in_progress", "completed"]
            },
            "priority": {
                "type": "string",
                "description": "New priority level.",
                "enum": ["low", "medium", "high"]
            },
            "due_date": {
                "type": "string",
                "description": "New due date in natural language or ISO format."
            },
            "category": {
                "type": "string",
                "description": "New category."
            }
        },
        "required": ["task_identifier"]
    }
}

delete_task_declaration = {
    "name": "delete_task",
    "description": "Delete a task from the to-do list. Use this when user wants to remove a task permanently. Requires task identification.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_identifier": {
                "type": "string",
                "description": "Task title or unique identifier to find and delete the task."
            }
        },
        "required": ["task_identifier"]
    }
}

complete_task_declaration = {
    "name": "complete_task",
    "description": "Mark a task as completed. Use this when user says they finished a task, completed something, or wants to check off a task.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_identifier": {
                "type": "string",
                "description": "Task title or unique identifier to find and complete the task."
            }
        },
        "required": ["task_identifier"]
    }
}

search_tasks_declaration = {
    "name": "search_tasks",
    "description": "Search tasks by keywords in title or description. Use this when user is looking for specific tasks but doesn't remember exact details.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query - keywords to find in task titles or descriptions."
            }
        },
        "required": ["query"]
    }
}


# Export all declarations as a list
todo_declarations = [
    add_task_declaration,
    get_tasks_declaration,
    update_task_declaration,
    delete_task_declaration,
    complete_task_declaration,
    search_tasks_declaration
]


# ===== HELPER FUNCTIONS =====

def _parse_due_date(date_str: str) -> Optional[datetime]:
    """Parse natural language date strings into datetime objects"""
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    now = datetime.now()
    
    # Handle relative dates
    if date_str in ["today", "now"]:
        return now.replace(hour=23, minute=59, second=59)
    
    if date_str == "tomorrow":
        return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    
    # "in X days/weeks/months"
    match = re.match(r"in (\d+) (day|week|month)s?", date_str)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "day":
            return (now + timedelta(days=amount)).replace(hour=23, minute=59, second=59)
        elif unit == "week":
            return (now + timedelta(weeks=amount)).replace(hour=23, minute=59, second=59)
        elif unit == "month":
            return (now + timedelta(days=amount*30)).replace(hour=23, minute=59, second=59)
    
    # "next Monday", "next Friday", etc.
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(weekdays):
        if f"next {day}" in date_str:
            days_ahead = (i - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (now + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=59)
    
    # Try ISO format
    try:
        return datetime.fromisoformat(date_str)
    except:
        pass
    
    # Try common formats
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None


def _find_task_by_identifier(identifier: str):
    """Find a task by title or partial match"""
    # First try exact match
    tasks = _todo_app.search_tasks(identifier)
    if tasks:
        return tasks[0]
    
    # Try getting all tasks and find best match
    all_tasks = _todo_app.get_all_tasks()
    identifier_lower = identifier.lower()
    
    for task in all_tasks:
        if identifier_lower in task.title.lower():
            return task
    
    return None


# ===== TOOL FUNCTIONS =====

def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """Add a new task to the to-do list"""
    try:
        # Parse due date if provided
        parsed_due_date = _parse_due_date(due_date) if due_date else None
        
        task = _todo_app.create_task(
            title=title,
            description=description,
            priority=priority.lower(),
            due_date=parsed_due_date,
            category=category
        )
        
        # Format response
        response = f"Task added: '{task.title}'"
        
        if task.priority.value == "high":
            response += " with high priority"
        
        if task.due_date:
            due_str = _format_due_date(task.due_date)
            response += f", due {due_str}"
        
        if task.category:
            response += f" (Category: {task.category})"
        
        response += "."
        
        return response
        
    except Exception as e:
        return f"Failed to add task: {str(e)}"


def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = 10
) -> str:
    """Get tasks from the to-do list"""
    try:
        tasks = _todo_app.get_all_tasks(
            status=status,
            priority=priority,
            category=category,
            limit=limit
        )
        
        if not tasks:
            filter_desc = []
            if status:
                filter_desc.append(f"status: {status}")
            if priority:
                filter_desc.append(f"priority: {priority}")
            if category:
                filter_desc.append(f"category: {category}")
            
            if filter_desc:
                return f"No tasks found with {', '.join(filter_desc)}."
            return "Your to-do list is empty."
        
        # Build response
        response = f"You have {len(tasks)} task{'s' if len(tasks) > 1 else ''}:\n"
        
        for i, task in enumerate(tasks, 1):
            status_icon = "✅" if task.status.value == "completed" else "⏳"
            priority_marker = "🔴" if task.priority.value == "high" else "🟡" if task.priority.value == "medium" else "🟢"
            
            line = f"{i}. {status_icon} {priority_marker} {task.title}"
            
            if task.due_date:
                due_str = _format_due_date(task.due_date)
                line += f" (Due: {due_str})"
            
            response += line + "\n"
        
        return response.strip()
        
    except Exception as e:
        return f"Failed to get tasks: {str(e)}"


def update_task(
    task_identifier: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """Update an existing task"""
    try:
        task = _find_task_by_identifier(task_identifier)
        
        if not task:
            return f"Task '{task_identifier}' not found."
        
        # Parse due date if provided
        parsed_due_date = _parse_due_date(due_date) if due_date else None
        
        updated_task = _todo_app.update_task(
            task_id=task.id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=parsed_due_date,
            category=category
        )
        
        if updated_task:
            return f"Task updated: '{updated_task.title}'"
        else:
            return f"Failed to update task '{task_identifier}'"
            
    except Exception as e:
        return f"Failed to update task: {str(e)}"


def delete_task(task_identifier: str) -> str:
    """Delete a task from the to-do list"""
    try:
        task = _find_task_by_identifier(task_identifier)
        
        if not task:
            return f"Task '{task_identifier}' not found."
        
        title = task.title
        success = _todo_app.delete_task(task.id)
        
        if success:
            return f"Task deleted: '{title}'"
        else:
            return f"Failed to delete task '{task_identifier}'"
            
    except Exception as e:
        return f"Failed to delete task: {str(e)}"


def complete_task(task_identifier: str) -> str:
    """Mark a task as completed"""
    try:
        task = _find_task_by_identifier(task_identifier)
        
        if not task:
            return f"Task '{task_identifier}' not found."
        
        updated_task = _todo_app.complete_task(task.id)
        
        if updated_task:
            return f"Task completed: '{updated_task.title}'. Well done, Sir!"
        else:
            return f"Failed to complete task '{task_identifier}'"
            
    except Exception as e:
        return f"Failed to complete task: {str(e)}"


def search_tasks(query: str) -> str:
    """Search tasks by keywords"""
    try:
        tasks = _todo_app.search_tasks(query)
        
        if not tasks:
            return f"No tasks found matching '{query}'."
        
        response = f"Found {len(tasks)} task{'s' if len(tasks) > 1 else ''} matching '{query}':\n"
        
        for i, task in enumerate(tasks, 1):
            status_icon = "✅" if task.status.value == "completed" else "⏳"
            priority_marker = "🔴" if task.priority.value == "high" else "🟡" if task.priority.value == "medium" else "🟢"
            
            line = f"{i}. {status_icon} {priority_marker} {task.title}"
            
            if task.due_date:
                due_str = _format_due_date(task.due_date)
                line += f" (Due: {due_str})"
            
            response += line + "\n"
        
        return response.strip()
        
    except Exception as e:
        return f"Failed to search tasks: {str(e)}"


def get_tasks_data(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = 10
) -> dict:
    """Get tasks data for HUD display (internal function)"""
    try:
        tasks = _todo_app.get_all_tasks(status, priority, category, limit)
        stats = _todo_app.get_statistics()
        
        return {
            'tasks': [task.to_dict() for task in tasks],
            'statistics': stats,
            'count': len(tasks)
        }
    except Exception as e:
        print(f"Error getting tasks data: {e}")
        return {'tasks': [], 'statistics': {}, 'count': 0}


def _format_due_date(due_date: datetime) -> str:
    """Format due date for display"""
    now = datetime.now()
    diff = (due_date - now).days
    
    if diff < 0:
        return f"{abs(diff)} day{'s' if abs(diff) > 1 else ''} overdue"
    elif diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff < 7:
        return f"in {diff} days"
    else:
        return due_date.strftime("%B %d, %Y")
