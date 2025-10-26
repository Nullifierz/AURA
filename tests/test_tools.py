"""
Test script for the new modular tools structure.
Run this to verify everything is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    try:
        from core.tools import (
            get_calendar_events,
            get_weather,
            get_weather_data,
            get_time,
            get_date,
            TOOL_DECLARATIONS,
            TOOL_FUNCTIONS
        )
        print("✅ All imports successful")
        print(f"   - Loaded {len(TOOL_DECLARATIONS)} tool declarations")
        print(f"   - Registered {len(TOOL_FUNCTIONS)} tool functions")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tool_declarations():
    """Test that tool declarations are properly formatted."""
    print("\nTesting tool declarations...")
    try:
        from core.tools import TOOL_DECLARATIONS
        
        for decl in TOOL_DECLARATIONS:
            assert "name" in decl, f"Missing 'name' in declaration"
            assert "description" in decl, f"Missing 'description' in {decl.get('name')}"
            assert "parameters" in decl, f"Missing 'parameters' in {decl.get('name')}"
            print(f"✅ {decl['name']}: Valid declaration")
        
        return True
    except Exception as e:
        print(f"❌ Declaration test failed: {e}")
        return False

def test_time_tools():
    """Test time and date tools (no API required)."""
    print("\nTesting time tools...")
    try:
        from core.tools import get_time, get_date
        
        current_time = get_time()
        current_date = get_date()
        
        print(f"✅ get_time(): {current_time}")
        print(f"✅ get_date(): {current_date}")
        
        assert "WIB" in current_time, "Time should include WIB timezone"
        assert len(current_date) > 10, "Date should be formatted as full date"
        
        return True
    except Exception as e:
        print(f"❌ Time tools failed: {e}")
        return False

def test_brain_initialization():
    """Test Brain initialization with new tools."""
    print("\nTesting Brain initialization...")
    try:
        from core.brain import Brain
        
        brain = Brain()
        print(f"✅ Brain initialized successfully")
        print(f"   - Model: {brain.client}")
        print(f"   - Tools loaded: {brain.tools}")
        
        return True
    except Exception as e:
        print(f"❌ Brain initialization failed: {e}")
        return False

def test_tool_registry():
    """Test that tool registry matches declarations."""
    print("\nTesting tool registry...")
    try:
        from core.tools import TOOL_DECLARATIONS, TOOL_FUNCTIONS
        
        # Extract tool names from declarations
        declared_names = {decl["name"] for decl in TOOL_DECLARATIONS}
        
        # Check if all declared tools have implementations
        for name in declared_names:
            assert name in TOOL_FUNCTIONS, f"Tool '{name}' declared but not in TOOL_FUNCTIONS"
            print(f"✅ {name}: Declared and implemented")
        
        return True
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AURA Tools Module Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_tool_declarations,
        test_time_tools,
        test_tool_registry,
        test_brain_initialization,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All tests passed! The tools module is working correctly.")
        print("\nNext steps:")
        print("1. Delete old core/tools.py file (no longer needed)")
        print("2. Test with actual API calls: python main.py")
        print("3. Try asking: 'What time is it?' or 'What's the weather?'")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
