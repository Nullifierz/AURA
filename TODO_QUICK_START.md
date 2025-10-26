# 🚀 Quick Start Guide - To-Do App

## Installation Complete! ✅

The To-Do App is now fully integrated with AURA. Here's how to use it:

## 💬 Natural Language Commands

### **Adding Tasks**
```
✅ "Add a task to buy groceries tomorrow"
✅ "Remind me to call the dentist next Friday"
✅ "I need to finish the AURA project with high priority"
✅ "Add a high priority task to review code by next Monday"
✅ "Remember to workout today"
```

### **Viewing Tasks**
```
✅ "Show me my to-do list"
✅ "What tasks do I have?"
✅ "Show me my high priority tasks"
✅ "What's pending in my personal category?"
✅ "Show me completed tasks"
```

### **Managing Tasks**
```
✅ "Mark the groceries task as completed"
✅ "I finished the workout"
✅ "Delete the dentist task"
✅ "Change the AURA project to low priority"
✅ "Update the groceries task to tomorrow"
```

### **Searching**
```
✅ "Find tasks about AURA"
✅ "Search for work tasks"
✅ "Look for tasks with 'meeting'"
```

## 🎨 What You'll See

### **In Chat (AURA's Voice Response)**
```
AURA: "Task added: 'Buy groceries' with high priority, due tomorrow, Sir."
```

### **In HUD (Visual Display)**
```
┌─────────────────────┐
│  Task Statistics    │
├─────────────────────┤
│ ⏳ Pending: 3       │
│ ✅ Completed: 1     │
└─────────────────────┘

┌──────────┬────────────────────┬──────────────┬─────────────┐
│ Priority │ Task               │ Due Date     │ Status      │
├──────────┼────────────────────┼──────────────┼─────────────┤
│ 🔴 HIGH  │ Buy groceries      │ 📅 Tomorrow  │ ⏳ Pending  │
│ 🔴 HIGH  │ Finish AURA project│ Oct 31, 2025 │ ⏳ Pending  │
│ 🟡 MEDIUM│ Call dentist       │ In 3 days    │ ⏳ Pending  │
└──────────┴────────────────────┴──────────────┴─────────────┘
```

## 📅 Date Formats Supported

**Relative:**
- "today", "tomorrow"
- "in 3 days", "in 2 weeks"
- "next Monday", "next Friday"

**Absolute:**
- "2025-10-30"
- "30/10/2025"
- "October 30, 2025"

## 🎯 Priority Levels

- **🔴 HIGH**: Urgent, important tasks (highlighted in HUD)
- **🟡 MEDIUM**: Normal tasks (default)
- **🟢 LOW**: Nice-to-have tasks

## 📂 Categories (Examples)

- `personal` - Personal tasks
- `work` - Work-related
- `shopping` - Shopping lists
- `health` - Health appointments
- `learning` - Study/reading tasks

## 🧪 Test It Now!

Try these commands with AURA:

1. **Add your first task:**
   ```
   "Add a task to test the to-do app with high priority"
   ```

2. **View your tasks:**
   ```
   "Show me my tasks"
   ```

3. **Complete it:**
   ```
   "Mark the test task as completed"
   ```

## 📊 Features

✅ **11 AI tools** (5 original + 6 To-Do)
✅ **Natural language** date parsing
✅ **Smart filtering** by status, priority, category
✅ **Visual HUD** with color-coded priorities
✅ **SQLite database** for reliable storage
✅ **Search functionality** by keywords
✅ **Overdue tracking** with warnings
✅ **Task statistics** at a glance

## 🛠️ Technical Details

- **Database**: `data/apps/todo/todo.db` (auto-created)
- **Total Tools**: 11 (verified ✓)
- **Backend**: SQLite3 with indexed queries
- **Frontend**: Auto-updating HUD display
- **AI Integration**: Full Gemini function calling

## 📝 Notes

- Tasks persist across sessions (saved to database)
- HUD updates automatically when you use task commands
- High priority pending tasks are highlighted with cyan glow
- Emojis in responses are sanitized for TTS compatibility
- Database is excluded from git (data security)

---

**🎊 Ready to use! Start managing your tasks with AURA!**

For detailed documentation, see: `TODO_APP_README.md`
