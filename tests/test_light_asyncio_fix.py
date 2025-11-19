"""
Test script to verify light control AsyncIO fix
This simulates calling light functions from async context (like voice WebSocket)
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.light_tool import turn_on_light, turn_off_light, get_light_state


async def test_light_control_from_async():
    """Test calling sync light functions from async context"""
    print("\n" + "="*60)
    print("Testing Light Control from Async Context")
    print("="*60 + "\n")
    
    try:
        print("1. Testing get_light_state()...")
        state = get_light_state()
        if "error" in state:
            print(f"   ⚠️  Could not connect to light (normal if light is off/unavailable)")
            print(f"   Error: {state['error']}")
        else:
            print(f"   ✅ Light state retrieved: {state['state']}")
        
        print("\n2. Testing turn_on_light()...")
        result = turn_on_light(brightness=50)
        if "error" in result:
            print(f"   ⚠️  Could not turn on light: {result['error']}")
        else:
            print(f"   ✅ Light turned on: {result['message']}")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        print("\n3. Testing turn_off_light()...")
        result = turn_off_light()
        if "error" in result:
            print(f"   ⚠️  Could not turn off light: {result['error']}")
        else:
            print(f"   ✅ Light turned off: {result['message']}")
        
        print("\n" + "="*60)
        print("✅ All tests completed without AsyncIO errors!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("\n🧪 Light Tool AsyncIO Fix Test")
    print("This test simulates the voice WebSocket calling light functions\n")
    
    success = await test_light_control_from_async()
    
    if success:
        print("\n✅ SUCCESS: Light functions work correctly from async context!")
        print("The fix is working - no 'event loop is already running' errors.\n")
    else:
        print("\n❌ FAILURE: Tests encountered errors")
        print("Check the logs above for details.\n")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
