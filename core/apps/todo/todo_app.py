"""
To-Do App main logic
Provides high-level CRUD operations for task management
"""

import uuid
from datetime import datetime
from typing import List, Optional
from .models import Task, TaskStatus, TaskPriority
from .todo_storage import TodoStorage


class TodoApp:
    """Main To-Do application class"""
    
    def __init__(self, db_path: str = "data/apps/todo/todo.db"):
        """Initialize To-Do app with storage backend"""
        self.storage = TodoStorage(db_path)
    
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Task:
        """Create a new task"""
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority(priority.lower()),
            due_date=due_date,
            category=category,
            tags=tags or []
        )
        
        success = self.storage.add_task(task)
        if success:
            return task
        else:
            raise Exception("Failed to create task")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.storage.get_task(task_id)
    
    def get_all_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """Get all tasks with optional filters"""
        return self.storage.get_all_tasks(status, priority, category, limit)
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Task]:
        """Update an existing task"""
        task = self.storage.get_task(task_id)
        if not task:
            return None
        
        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = TaskStatus(status.lower())
        if priority is not None:
            task.priority = TaskPriority(priority.lower())
        if due_date is not None:
            task.due_date = due_date
        if category is not None:
            task.category = category
        if tags is not None:
            task.tags = tags
        
        success = self.storage.update_task(task)
        return task if success else None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        return self.storage.delete_task(task_id)
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        return self.update_task(task_id, status="completed")
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        return self.storage.search_tasks(query)
    
    def get_statistics(self) -> dict:
        """Get task statistics"""
        return self.storage.get_statistics()
    
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """Get all pending tasks"""
        return self.get_all_tasks(status="pending", limit=limit)
    
    def get_high_priority_tasks(self, limit: Optional[int] = None) -> List[Task]:
        """Get all high priority tasks"""
        return self.get_all_tasks(priority="high", limit=limit)
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks (past due date and not completed)"""
        tasks = self.get_all_tasks()
        now = datetime.now()
        return [
            task for task in tasks 
            if task.due_date and task.due_date < now and task.status != TaskStatus.COMPLETED
        ]
