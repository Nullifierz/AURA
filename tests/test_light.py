"""
Test script for smart light integration
Tests all light control functions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.tools.light_tool import (
    turn_on_light,
    turn_off_light,
    get_light_state,
    set_brightness,
    set_color,
    set_scene
)
import time


def test_basic_control():
    """Test basic on/off control"""
    print("\n=== Testing Basic Control ===")
    
    # Turn on
    print("\n1. Turning on light...")
    result = turn_on_light()
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Get state
    print("\n2. Getting light state...")
    result = get_light_state()
    print(f"   Result: {result}")
    time.sleep(1)
    
    # Turn off
    print("\n3. Turning off light...")
    result = turn_off_light()
    print(f"   Result: {result}")
    time.sleep(2)


def test_brightness():
    """Test brightness control"""
    print("\n=== Testing Brightness ===")
    
    # Turn on with brightness
    print("\n1. Turning on at 50% brightness (128)...")
    result = set_brightness(128)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Max brightness
    print("\n2. Setting to max brightness (255)...")
    result = set_brightness(255)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Low brightness
    print("\n3. Setting to low brightness (50)...")
    result = set_brightness(50)
    print(f"   Result: {result}")
    time.sleep(2)


def test_colors():
    """Test color control"""
    print("\n=== Testing Colors ===")
    
    # Red
    print("\n1. Setting color to RED...")
    result = set_color(255, 0, 0)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Green
    print("\n2. Setting color to GREEN...")
    result = set_color(0, 255, 0)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Blue
    print("\n3. Setting color to BLUE...")
    result = set_color(0, 0, 255)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Purple
    print("\n4. Setting color to PURPLE...")
    result = set_color(128, 0, 128)
    print(f"   Result: {result}")
    time.sleep(2)


def test_scenes():
    """Test scene control"""
    print("\n=== Testing Scenes ===")
    
    # Party scene
    print("\n1. Setting PARTY scene (4)...")
    result = set_scene(4)
    print(f"   Result: {result}")
    time.sleep(3)
    
    # Focus scene
    print("\n2. Setting FOCUS scene (15)...")
    result = set_scene(15)
    print(f"   Result: {result}")
    time.sleep(3)
    
    # Relax scene
    print("\n3. Setting RELAX scene (16)...")
    result = set_scene(16)
    print(f"   Result: {result}")
    time.sleep(3)


def test_temperature():
    """Test color temperature"""
    print("\n=== Testing Color Temperature ===")
    
    # Warm white
    print("\n1. Setting WARM WHITE (2700K)...")
    result = turn_on_light(color_temp=2700)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Cool white
    print("\n2. Setting COOL WHITE (6500K)...")
    result = turn_on_light(color_temp=6500)
    print(f"   Result: {result}")
    time.sleep(2)
    
    # Neutral
    print("\n3. Setting NEUTRAL (4000K)...")
    result = turn_on_light(color_temp=4000)
    print(f"   Result: {result}")
    time.sleep(2)


def main():
    print("=" * 60)
    print("AURA Smart Light Integration Test")
    print("=" * 60)
    
    try:
        # Run all tests
        test_basic_control()
        test_brightness()
        test_colors()
        test_scenes()
        test_temperature()
        
        # Final cleanup
        print("\n=== Test Complete ===")
        print("\nTurning off light...")
        turn_off_light()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nMake sure:")
        print("1. Light is powered on")
        print("2. Light is connected to network")
        print("3. IP address is correct in core/tools/light_tool.py")
        

if __name__ == "__main__":
    main()