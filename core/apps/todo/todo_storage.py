"""
SQLite storage backend for To-Do App
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from .models import Task, TaskStatus, TaskPriority


class TodoStorage:
    """SQLite storage for tasks"""
    
    def __init__(self, db_path: str = "data/apps/todo/todo.db"):
        """Initialize storage with database path"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    due_date TEXT,
                    category TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON tasks(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_priority 
                ON tasks(priority)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_due_date 
                ON tasks(due_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_category 
                ON tasks(category)
            """)
            
            conn.commit()
    
    def _task_from_row(self, row: tuple) -> Task:
        """Convert database row to Task object"""
        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            status=TaskStatus(row[3]),
            priority=TaskPriority(row[4]),
            due_date=datetime.fromisoformat(row[5]) if row[5] else None,
            category=row[6],
            created_at=datetime.fromisoformat(row[7]),
            updated_at=datetime.fromisoformat(row[8]),
            tags=json.loads(row[9]) if row[9] else []
        )
    
    def add_task(self, task: Task) -> bool:
        """Add a new task to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks 
                    (id, title, description, status, priority, due_date, category, created_at, updated_at, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task.id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.due_date.isoformat() if task.due_date else None,
                    task.category,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                    json.dumps(task.tags)
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                return self._task_from_row(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting task: {e}")
            return None
    
    def get_all_tasks(
        self, 
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """Get all tasks with optional filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if priority:
                    query += " AND priority = ?"
                    params.append(priority)
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                # Order by priority (high first), then due date
                query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, due_date ASC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._task_from_row(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting tasks: {e}")
            return []
    
    def update_task(self, task: Task) -> bool:
        """Update an existing task"""
        try:
            task.updated_at = datetime.now()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tasks 
                    SET title = ?, description = ?, status = ?, priority = ?, 
                        due_date = ?, category = ?, updated_at = ?, tags = ?
                    WHERE id = ?
                """, (
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.due_date.isoformat() if task.due_date else None,
                    task.category,
                    task.updated_at.isoformat(),
                    json.dumps(task.tags),
                    task.id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting task: {e}")
            return False
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                search_pattern = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM tasks 
                    WHERE title LIKE ? OR description LIKE ?
                    ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
                """, (search_pattern, search_pattern))
                rows = cursor.fetchall()
                return [self._task_from_row(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error searching tasks: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Get task statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count by status
                cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
                for status, count in cursor.fetchall():
                    stats[status] = count
                
                # Total tasks
                cursor.execute("SELECT COUNT(*) FROM tasks")
                stats['total'] = cursor.fetchone()[0]
                
                # Overdue tasks
                cursor.execute("""
                    SELECT COUNT(*) FROM tasks 
                    WHERE due_date < ? AND status != 'completed'
                """, (datetime.now().isoformat(),))
                stats['overdue'] = cursor.fetchone()[0]
                
                return stats
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {}
