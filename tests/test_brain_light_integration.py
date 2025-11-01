"""
Test script to verify brain.py handles light tool results correctly.
Tests the fix for "unhashable type: 'slice'" error.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain import Brain

def test_light_result_handling():
    """Test that brain can handle dict results from light tools."""
    print("Testing light tool result handling in brain.py...")
    
    brain = Brain()
    
    # Simulate light tool results (dict format)
    test_results = [
        {
            "name": "turn_on_light",
            "args": {"brightness": 128},
            "result": {"success": True, "message": "Light turned on", "light": "default"}
        },
        {
            "name": "get_light_state",
            "args": {},
            "result": {
                "success": True,
                "light": "default",
                "state": {
                    "on": True,
                    "brightness": 200,
                    "rgb": [255, 128, 0],
                    "color_temp": 4000,
                    "scene_id": 4
                }
            }
        },
        {
            "name": "set_color",
            "args": {"r": 255, "g": 0, "b": 0},
            "result": {"success": True, "message": "Color set to red", "light": "default"}
        }
    ]
    
    print("\n✓ Testing dict result handling...")
    for test in test_results:
        try:
            # Test the HUD processing
            brain._process_tool_call_for_hud(test["name"], test["args"], test["result"])
            print(f"  ✓ {test['name']}: SUCCESS")
        except Exception as e:
            print(f"  ✗ {test['name']}: FAILED - {e}")
            return False
    
    # Check HUD sections were created
    if len(brain.hud_sections) > 0:
        print(f"\n✓ HUD sections created: {len(brain.hud_sections)}")
        for section in brain.hud_sections:
            print(f"  - {section['title']}")
    else:
        print("\n⚠ No HUD sections created (this is OK)")
    
    print("\n✅ All tests passed! The 'unhashable type: slice' error is fixed.")
    return True

if __name__ == "__main__":
    success = test_light_result_handling()
    sys.exit(0 if success else 1)
