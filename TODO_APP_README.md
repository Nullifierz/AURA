# 📋 To-Do App - AURA AI Assistant

A comprehensive task management system integrated with AURA's AI capabilities.

## ✨ Features

### **AI-Powered Task Management**
- **Natural Language Processing**: Add tasks using conversational language
  - "Add a task to buy groceries tomorrow"
  - "Remind me to call the dentist next Friday"
  - "I need to finish the AURA project with high priority"

### **Smart Task Organization**
- **Priority Levels**: Low, Medium, High (with visual indicators)
- **Status Tracking**: Pending, In Progress, Completed
- **Categories**: Personal, Work, Shopping, Health, Learning, etc.
- **Due Dates**: Natural language support ("tomorrow", "next Monday", "in 3 days")
- **Tags**: Organize tasks with custom tags

### **Intelligent Filtering**
- Filter by status, priority, or category
- Search tasks by keywords
- Automatic sorting (high priority first, then by due date)
- Highlight overdue and urgent tasks

### **Visual HUD Display**
- Task statistics at a glance
- Professional table view with color-coded priorities
- Due date indicators (overdue warnings, today, tomorrow)
- Interactive display synced with AI responses

## 🏗️ Architecture

```
core/apps/todo/
├── __init__.py           # Package exports
├── models.py             # Data models (Task, TaskStatus, TaskPriority)
├── todo_storage.py       # SQLite database operations
├── todo_app.py           # Main application logic
└── todo_tool.py          # AI tool declarations & functions

data/apps/todo/
└── todo.db               # SQLite database (auto-created)
```

## 📊 Database Schema

**Tasks Table:**
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,           -- UUID
    title TEXT NOT NULL,           -- Task title
    description TEXT,              -- Optional details
    status TEXT NOT NULL,          -- pending/in_progress/completed
    priority TEXT NOT NULL,        -- low/medium/high
    due_date TEXT,                 -- ISO datetime or NULL
    category TEXT,                 -- Optional category
    created_at TEXT NOT NULL,      -- ISO datetime
    updated_at TEXT NOT NULL,      -- ISO datetime
    tags TEXT                      -- JSON array of strings
);
```

**Indexes:**
- `idx_status` on status
- `idx_priority` on priority
- `idx_due_date` on due_date
- `idx_category` on category

## 🛠️ AI Tools

### **1. add_task**
Add a new task to the to-do list.

**Parameters:**
- `title` (required): Task title
- `description` (optional): Detailed notes
- `priority` (optional): "low", "medium", or "high" (default: "medium")
- `due_date` (optional): Natural language date
- `category` (optional): Task category

**Example:**
```
User: "Add a task to buy groceries tomorrow with high priority"
AURA: "Task added: 'Buy groceries' with high priority, due tomorrow."
```

### **2. get_tasks**
Retrieve tasks with optional filters.

**Parameters:**
- `status` (optional): "pending", "in_progress", or "completed"
- `priority` (optional): "low", "medium", or "high"
- `category` (optional): Category name
- `limit` (optional): Maximum number of tasks (default: 10)

**Example:**
```
User: "Show me my high priority tasks"
AURA: "You have 2 high priority tasks, Sir. [HUD displays table]"
```

### **3. update_task**
Modify an existing task.

**Parameters:**
- `task_identifier` (required): Task title or partial match
- `title` (optional): New title
- `description` (optional): New description
- `status` (optional): New status
- `priority` (optional): New priority
- `due_date` (optional): New due date
- `category` (optional): New category

**Example:**
```
User: "Change the groceries task to medium priority"
AURA: "Task updated: 'Buy groceries'"
```

### **4. complete_task**
Mark a task as completed.

**Parameters:**
- `task_identifier` (required): Task title or partial match

**Example:**
```
User: "Mark the groceries task as done"
AURA: "Task completed: 'Buy groceries'. Well done, Sir!"
```

### **5. delete_task**
Remove a task from the list.

**Parameters:**
- `task_identifier` (required): Task title or partial match

**Example:**
```
User: "Delete the dentist task"
AURA: "Task deleted: 'Call dentist'"
```

### **6. search_tasks**
Find tasks by keywords.

**Parameters:**
- `query` (required): Search keywords

**Example:**
```
User: "Find tasks about AURA"
AURA: "Found 1 task matching 'AURA': [task details]"
```

## 📅 Natural Language Date Parsing

The To-Do App supports various date formats:

**Relative Dates:**
- `today` → End of today
- `tomorrow` → End of tomorrow
- `in 3 days` → 3 days from now
- `in 2 weeks` → 2 weeks from now
- `in 1 month` → Approximately 30 days from now

**Weekday References:**
- `next Monday` → Next occurrence of Monday
- `next Friday` → Next occurrence of Friday

**Explicit Dates:**
- `2025-10-30` → ISO format (YYYY-MM-DD)
- `30/10/2025` → DD/MM/YYYY
- `10/30/2025` → MM/DD/YYYY

## 🎨 HUD Display

### **Task Statistics Section**
```
Task Statistics
⏳ Pending: 3
🔄 In Progress: 1
✅ Completed: 2
⚠️ Overdue: 0
```

### **Task Table Section**
```
To-Do List
┌──────────┬────────────────────┬──────────────┬─────────────┐
│ Priority │ Task               │ Due Date     │ Status      │
├──────────┼────────────────────┼──────────────┼─────────────┤
│ 🔴 HIGH  │ Buy groceries      │ 📅 Tomorrow  │ ⏳ Pending  │
│ 🔴 HIGH  │ Finish AURA project│ Oct 31, 2025 │ ⏳ Pending  │
│ 🟡 MEDIUM│ Call dentist       │ In 3 days    │ ⏳ Pending  │
│ 🟢 LOW   │ Read documentation │ No deadline  │ ✅ Completed│
└──────────┴────────────────────┴──────────────┴─────────────┘
```

**Visual Indicators:**
- 🔴 High priority (red glow if pending)
- 🟡 Medium priority
- 🟢 Low priority
- ⏳ Pending
- 🔄 In Progress
- ✅ Completed
- ⚠️ Overdue warning

## 💻 Programmatic Usage

### **Python API**
```python
from core.apps.todo import TodoApp

# Initialize app
app = TodoApp()

# Create task
task = app.create_task(
    title="Buy groceries",
    priority="high",
    due_date=datetime.now() + timedelta(days=1),
    category="personal"
)

# Get all tasks
tasks = app.get_all_tasks()

# Get filtered tasks
high_priority = app.get_all_tasks(priority="high")
pending = app.get_pending_tasks()
overdue = app.get_overdue_tasks()

# Update task
app.update_task(task.id, status="in_progress")

# Complete task
app.complete_task(task.id)

# Delete task
app.delete_task(task.id)

# Search tasks
results = app.search_tasks("groceries")

# Get statistics
stats = app.get_statistics()
```

### **AI Tool Functions**
```python
from core.tools import add_task, get_tasks, complete_task

# Add task via AI tool
add_task(
    title="Buy groceries",
    priority="high",
    due_date="tomorrow",
    category="personal"
)

# Get tasks
result = get_tasks(status="pending", limit=5)

# Complete task
complete_task("Buy groceries")
```

## 🧪 Testing

Run the test suite:
```bash
python test_todo.py
```

Expected output:
```
✅ ALL TESTS PASSED!
```

## 🎯 Example Conversations

**Adding Tasks:**
```
User: "I need to buy groceries tomorrow"
AURA: "Task added: 'Buy groceries', due tomorrow, Sir."
```

**Checking Tasks:**
```
User: "What's on my to-do list?"
AURA: "You have 4 pending tasks, Sir. [HUD shows full list]"
```

**High Priority:**
```
User: "Show me my urgent tasks"
AURA: "You have 2 high priority tasks, Sir. [HUD displays]"
```

**Completing Tasks:**
```
User: "I finished the groceries"
AURA: "Task completed: 'Buy groceries'. Well done, Sir!"
```

**Searching:**
```
User: "Find tasks about AURA"
AURA: "Found 1 task matching 'AURA': Finish AURA project."
```

## 🔧 Configuration

No additional configuration required. The To-Do App:
- Auto-creates database on first use
- Stores data in `data/apps/todo/todo.db`
- Integrates automatically with AURA's AI brain
- HUD displays update automatically

## 🚀 Future Enhancements

Potential additions:
- [ ] Recurring tasks (daily, weekly, monthly)
- [ ] Task reminders with notifications
- [ ] Subtasks and task dependencies
- [ ] Task templates
- [ ] Export to CSV/JSON
- [ ] Task sharing and collaboration
- [ ] Time tracking per task
- [ ] Task analytics and productivity insights

## 📝 Notes

- Database is excluded from git via `.gitignore`
- All timestamps use local timezone
- Task IDs are UUID v4
- Emoji icons are sanitized for TTS compatibility
- HUD auto-highlights high priority pending tasks

---

**Built with ❤️ for AURA AI Assistant**
