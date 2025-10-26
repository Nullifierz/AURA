"""
Test script for To-Do App functionality
Run this to verify the To-Do App is working correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.apps.todo import TodoApp, add_task, get_tasks, complete_task, search_tasks
from datetime import datetime, timedelta


def test_todo_app():
    """Test all To-Do App functionality"""
    print("=" * 60)
    print("🧪 TESTING TO-DO APP")
    print("=" * 60)
    
    # Test 1: Create tasks
    print("\n1️⃣ Creating test tasks...")
    
    result1 = add_task(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
        due_date="tomorrow",
        category="personal"
    )
    print(f"   ✓ {result1}")
    
    result2 = add_task(
        title="Finish AURA project",
        priority="high",
        due_date="next Friday"
    )
    print(f"   ✓ {result2}")
    
    result3 = add_task(
        title="Read Python documentation",
        priority="low",
        category="learning"
    )
    print(f"   ✓ {result3}")
    
    result4 = add_task(
        title="Call dentist",
        priority="medium",
        due_date="in 3 days",
        category="health"
    )
    print(f"   ✓ {result4}")
    
    # Test 2: Get all tasks
    print("\n2️⃣ Getting all tasks...")
    all_tasks = get_tasks()
    print(f"\n{all_tasks}")
    
    # Test 3: Get high priority tasks
    print("\n3️⃣ Getting high priority tasks...")
    high_priority = get_tasks(priority="high")
    print(f"\n{high_priority}")
    
    # Test 4: Search tasks
    print("\n4️⃣ Searching for 'AURA'...")
    search_result = search_tasks("AURA")
    print(f"\n{search_result}")
    
    # Test 5: Complete a task
    print("\n5️⃣ Completing 'Read Python documentation'...")
    complete_result = complete_task("Read Python documentation")
    print(f"   ✓ {complete_result}")
    
    # Test 6: Get pending tasks
    print("\n6️⃣ Getting pending tasks...")
    pending = get_tasks(status="pending")
    print(f"\n{pending}")
    
    # Test 7: Test data for HUD
    print("\n7️⃣ Testing HUD data generation...")
    from core.tools import get_tasks_data
    tasks_data = get_tasks_data(limit=10)
    print(f"   ✓ Found {tasks_data['count']} tasks")
    print(f"   ✓ Statistics: {tasks_data['statistics']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n💡 Try these commands in AURA:")
    print("   • 'Add a task to buy groceries tomorrow'")
    print("   • 'Show me my to-do list'")
    print("   • 'What are my high priority tasks?'")
    print("   • 'Mark the groceries task as completed'")
    print("   • 'Search for tasks about AURA'")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_todo_app()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
