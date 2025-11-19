# Light Tool AsyncIO Fix - November 2, 2025

## Problem Description

When voice commands triggered light control functions (e.g., "turn off the lights"), the system encountered AsyncIO errors:

```
ERROR - Error executing turn_off_light: This event loop is already running
RuntimeWarning: coroutine 'turn_off_light_async' was never awaited
```

## Root Cause Analysis

### Call Stack
1. **Voice WebSocket** (async context) receives command
2. `voice_websocket._process_command()` (async) calls `brain.generate()` (sync)
3. `brain.generate()` (sync) calls `turn_off_light()` (sync)
4. `turn_off_light()` calls `_run_async(turn_off_light_async())` 
5. `_run_async()` tries to use `loop.run_until_complete()`
6. ❌ **FAILS**: Cannot call `run_until_complete()` when already in async context

### The Nested Event Loop Problem

```
FastAPI/WebSocket (async loop running)
  └─> voice_websocket._process_command() [ASYNC]
       └─> brain.generate() [SYNC]
            └─> turn_off_light() [SYNC]
                 └─> _run_async() tries loop.run_until_complete()
                     └─> ❌ ERROR: Event loop already running
```

**Key Issue**: You cannot use `run_until_complete()` from within an already-running event loop. This is a Python asyncio restriction.

## Solution Implemented

Modified `_run_async()` helper in `core/tools/light_tool.py` to detect the execution context and handle both cases:

### 1. **When Called from Async Context** (e.g., Voice WebSocket)
- Detect running loop with `asyncio.get_running_loop()`
- Create a **new thread** with its own event loop
- Run the coroutine in that separate thread
- Wait for completion and return result
- This avoids nested event loop issues

### 2. **When Called from Sync Context** (e.g., REST API)
- No running loop exists
- Create/reuse event loop normally
- Use `run_until_complete()` as before
- Windows-specific ProactorEventLoop handling

## Code Changes

**File**: `core/tools/light_tool.py`

### Before (Broken)
```python
def _run_async(coro):
    """Run async code with proper event loop handling for Windows"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)  # ❌ Fails if loop already running
```

### After (Fixed)
```python
def _run_async(coro):
    """Run async code with proper event loop handling for Windows"""
    try:
        # Check if we're already in an async context with a running loop
        loop = asyncio.get_running_loop()
        
        # If we get here, there's a running loop - use separate thread
        result = [None]
        exception = [None]
        
        def run_in_thread():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result[0] = new_loop.run_until_complete(coro)
            except Exception as e:
                exception[0] = e
            finally:
                new_loop.close()
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()
        
        if exception[0]:
            raise exception[0]
        return result[0]
        
    except RuntimeError:
        # No running loop - create/use one directly
        loop = asyncio.get_event_loop()
        # ... original logic for sync context ...
        return loop.run_until_complete(coro)
```

**Added Import**:
```python
import threading
```

## How It Works

### Detection Logic
- `asyncio.get_running_loop()` raises `RuntimeError` if no loop is running
- If it succeeds, we're in an async context → use thread approach
- If it fails, we're in sync context → use direct approach

### Thread-Based Execution (Async Context)
1. Create result and exception containers (lists for thread-safe mutation)
2. Define `run_in_thread()` that creates its own event loop
3. Start thread, run coroutine, capture result/exception
4. Join thread to wait for completion
5. Raise exception if any, otherwise return result

### Direct Execution (Sync Context)
- Original behavior preserved
- Create/reuse event loop
- Windows ProactorEventLoop handling
- `run_until_complete()` works fine here

## Testing

### Manual Test Cases

**1. Voice Command** (Async Context)
```
User: "AURA, turn off the lights"
Expected: Lights turn off, no errors
```

**2. REST API** (Sync Context)
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"contents": "turn off the lights"}'
```
Expected: Works as before, no errors

**3. Multiple Rapid Commands**
```
User: "AURA, turn on the lights"
User: "AURA, set brightness to 50"
User: "AURA, turn off the lights"
```
Expected: All commands execute correctly without conflicts

## Expected Behavior After Fix

### Before Fix
```
2025-11-02 00:16:08 - core.brain - ERROR - Error executing turn_off_light: This event loop is already running
RuntimeWarning: coroutine 'turn_off_light_async' was never awaited
```

### After Fix
```
2025-11-02 00:20:15 - core.tools.light_tool - INFO - Turning off light: default
2025-11-02 00:20:15 - core.brain - INFO - Function turn_off_light executed successfully
```

## Related Files

- `core/tools/light_tool.py` - Fixed `_run_async()` helper
- `core/brain.py` - Calls light functions (no changes needed)
- `core/voice_websocket.py` - Provides async context (no changes needed)

## Why This Pattern Is Necessary

### The AsyncIO Golden Rule
> **You cannot call `run_until_complete()` from within a running event loop.**

### Our Architecture Requires Both Contexts
1. **Sync Tools**: Brain's function calling expects sync functions that return results immediately
2. **Async Hardware**: WiZ lights use async pywizlight library
3. **Mixed Execution**: Voice (async) and REST API (sync) both use same tools

### The Bridge Pattern
The `_run_async()` helper acts as a **sync-to-async bridge**:
- Makes async code callable from sync contexts
- Handles both execution environments transparently
- No changes needed to calling code

## Performance Considerations

### Thread Overhead
- Creating a thread has ~5-10ms overhead
- Acceptable for infrequent operations like light control
- Much better than crashing with AsyncIO errors

### Alternative Approaches Considered

1. ❌ **Make brain.generate() async**: Would break REST API compatibility
2. ❌ **Make all tools async**: Would require major refactoring
3. ✅ **Thread-based bridge**: Minimal changes, works in both contexts

## Future Improvements

If performance becomes an issue, consider:
1. Thread pool for reusing threads
2. Making brain.generate() async-aware with dual interfaces
3. Refactoring to full async architecture (major change)

For now, the thread-based solution is simple, robust, and sufficient.

## Verification Steps

1. Start AURA backend: `python main.py`
2. Open frontend in browser
3. Click voice button and say: "AURA, turn off the lights"
4. Check logs - should see NO "event loop is already running" errors
5. Verify lights actually turn off

## Related Issues

- See `VOICE_ASYNCIO_FIX.md` for WebSocket callback threading fix
- Both fixes use thread-based approaches to bridge sync/async contexts
- These patterns are consistent across the codebase now

---

**Status**: ✅ Fixed
**Date**: November 2, 2025
**Impact**: Voice commands can now control lights without AsyncIO errors
