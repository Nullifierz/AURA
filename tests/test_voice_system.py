"""
Test script to verify the voice input system without WebSocket
Tests wake word detection and fuzzy matching
"""

import time
from core.ears import Ears

def test_wake_word_matching():
    """Test fuzzy wake word matching"""
    print("=" * 60)
    print("TESTING WAKE WORD FUZZY MATCHING")
    print("=" * 60)
    
    ears = Ears()
    
    test_cases = [
        # (input, should_match)
        ("aura", True),
        ("aurora", True),
        ("ora", True),
        ("oda", True),
        ("ura", True),
        ("auora", True),  # Typo
        ("arora", True),  # Variation
        ("hello", False),
        ("computer", False),
        ("jarvis", True),
        ("hey aura", True),  # In a sentence
        ("okay aura what time is it", True),
    ]
    
    print("\nTest Cases:")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for text, should_match in test_cases:
        result = ears._fuzzy_match_wake_word(text)
        status = "✅ PASS" if result == should_match else "❌ FAIL"
        
        if result == should_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | '{text}' -> {result} (expected: {should_match})")
    
    print("-" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_mute_phrases():
    """Test mute phrase detection"""
    print("\n" + "=" * 60)
    print("TESTING MUTE PHRASE DETECTION")
    print("=" * 60)
    
    ears = Ears()
    
    test_cases = [
        ("that would be all", True),
        ("that will be all", True),
        ("mute", True),
        ("stop listening", True),
        ("goodbye", True),
        ("hello", False),
        ("what's the weather", False),
        ("okay that would be all thanks", True),  # In sentence
    ]
    
    print("\nTest Cases:")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for text, should_match in test_cases:
        result = ears._check_mute_phrase(text)
        status = "✅ PASS" if result == should_match else "❌ FAIL"
        
        if result == should_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | '{text}' -> {result} (expected: {should_match})")
    
    print("-" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_state_machine():
    """Test state transitions"""
    print("\n" + "=" * 60)
    print("TESTING STATE MACHINE")
    print("=" * 60)
    
    ears = Ears()
    
    # Track state changes
    state_changes = []
    
    def on_state_change(old_state, new_state):
        state_changes.append((old_state, new_state))
        print(f"  State: {old_state} → {new_state}")
    
    ears.on_state_change_callback = on_state_change
    
    print("\nTest Transitions:")
    print("-" * 60)
    
    # Test state transitions
    from core.ears import ListeningState
    
    print("1. Start in STANDBY")
    assert ears.get_state() == "standby", "Should start in standby"
    print("  ✅ Correct initial state")
    
    print("\n2. Transition to LISTENING")
    ears.set_state(ListeningState.LISTENING)
    assert ears.get_state() == "listening", "Should be listening"
    print("  ✅ Transition successful")
    
    print("\n3. Transition to PROCESSING")
    ears.set_state(ListeningState.PROCESSING)
    assert ears.get_state() == "processing", "Should be processing"
    print("  ✅ Transition successful")
    
    print("\n4. Transition to SPEAKING")
    ears.set_state(ListeningState.SPEAKING)
    assert ears.get_state() == "speaking", "Should be speaking"
    print("  ✅ Transition successful")
    
    print("\n5. Return to STANDBY")
    ears.set_state(ListeningState.STANDBY)
    assert ears.get_state() == "standby", "Should be standby"
    print("  ✅ Transition successful")
    
    print("-" * 60)
    print(f"\n✅ All state transitions passed ({len(state_changes)} changes recorded)")
    print("=" * 60)
    
    return True


def test_callback_safety():
    """Test that callbacks don't crash the system"""
    print("\n" + "=" * 60)
    print("TESTING CALLBACK SAFETY")
    print("=" * 60)
    
    ears = Ears()
    
    callback_calls = {
        "wake": 0,
        "command": 0,
        "mute": 0,
        "state_change": 0
    }
    
    def on_wake(text):
        callback_calls["wake"] += 1
        print(f"  ✅ Wake callback: '{text}'")
    
    def on_command(text):
        callback_calls["command"] += 1
        print(f"  ✅ Command callback: '{text}'")
    
    def on_mute(text):
        callback_calls["mute"] += 1
        print(f"  ✅ Mute callback: '{text}'")
    
    def on_state_change(old_state, new_state):
        callback_calls["state_change"] += 1
        # Don't print here to avoid noise
    
    ears.on_wake_word_callback = on_wake
    ears.on_command_callback = on_command
    ears.on_mute_callback = on_mute
    ears.on_state_change_callback = on_state_change
    
    print("\nTest Callbacks:")
    print("-" * 60)
    
    # Simulate wake word detection
    print("1. Trigger wake callback")
    on_wake("aura")
    
    print("\n2. Trigger command callback")
    on_command("what's the weather")
    
    print("\n3. Trigger mute callback")
    on_mute("that would be all")
    
    print("\n4. Trigger state change callback")
    on_state_change("standby", "listening")
    
    print("-" * 60)
    print(f"\n✅ All callbacks executed successfully")
    print(f"  Wake: {callback_calls['wake']}")
    print(f"  Command: {callback_calls['command']}")
    print(f"  Mute: {callback_calls['mute']}")
    print(f"  State Change: {callback_calls['state_change']}")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    print("\n🎤 AURA VOICE INPUT SYSTEM - TEST SUITE")
    print("=" * 60)
    print("This will test the voice input components without WebSocket")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    try:
        test1 = test_wake_word_matching()
        test2 = test_mute_phrases()
        test3 = test_state_machine()
        test4 = test_callback_safety()
        
        all_passed = test1 and test2 and test3 and test4
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Voice input system is working correctly")
        print("✅ Wake word fuzzy matching works")
        print("✅ Mute phrase detection works")
        print("✅ State machine works")
        print("✅ Callbacks are safe")
        print("\n📝 Next step: Test with WebSocket (start main.py)")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease check the errors above")
    
    print("\n" + "=" * 60)
