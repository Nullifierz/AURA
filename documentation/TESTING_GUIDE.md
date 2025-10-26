# 🧪 HUD Integration - Testing Guide

## Quick Test Setup

### 1. Start the Backend
```bash
cd d:\Personal\Hobi\AURA
python main.py
```

Expected output:
```
INFO - Starting AURA application
INFO - Initializing Brain with gemini-2.5-flash
INFO - Loaded 4 tool declarations
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Open Frontend
Open `d:\Personal\Hobi\AURA\frontend\index.html` in your browser

### 3. Test Queries

## Test Cases

### ✅ Test 1: Weather Query (Automatic HUD)

**Say or Type:**
```
"What's the weather in Jakarta?"
```

**Expected Behavior:**
1. ✅ AI responds: "The weather in Jakarta is..."
2. ✅ Audio plays through visualizer
3. ✅ **HUD automatically appears**
4. ✅ Shows 3 sections:
   - Weather Data (keyvalue)
   - Weather Icon (image)
   - Sun Times (keyvalue)

**Console Output:**
```javascript
Executing function: get_weather({'location': 'Jakarta', 'temperature': 'C'})
Processing HUD data for tool: get_weather
Updating HUD with tool data: [3 sections]
```

---

### ✅ Test 2: Different Locations

**Say or Type:**
```
"How's the weather in London?"
"Tell me Tokyo's temperature"
"Weather in New York"
```

**Expected:**
- Each query updates HUD with new location
- Old data replaced with fresh data
- Icon changes based on weather condition

---

### ✅ Test 3: Time Query

**Say or Type:**
```
"What time is it?"
```

**Expected Behavior:**
1. ✅ AI responds: "It's 10:15 AM WIB, Sir"
2. ✅ **HUD shows:**
   - Date & Time section
   - Current date, time, timezone

---

### ✅ Test 4: Calendar Query (if configured)

**Say or Type:**
```
"What's on my schedule?"
"Show my upcoming events"
```

**Expected Behavior:**
1. ✅ AI responds with events
2. ✅ **HUD shows:**
   - Upcoming Events section
   - Formatted list of calendar events

---

### ✅ Test 5: No Tools (Normal Chat)

**Say or Type:**
```
"Hello AURA"
"Tell me a joke"
"What can you do?"
```

**Expected Behavior:**
1. ✅ AI responds normally
2. ✅ Audio plays
3. ✅ **HUD does NOT appear** (no tools used)

---

### ✅ Test 6: Multiple Tools

**Say or Type:**
```
"What's the weather and what time is it?"
```

**Expected Behavior:**
1. ✅ AI calls both tools
2. ✅ **HUD shows both:**
   - Weather sections (3)
   - Time section (1)
   - Total: 4 sections

---

### ✅ Test 7: Manual HUD Refresh

**Steps:**
1. Click "HUD" button (bottom right)
2. Click refresh icon in HUD header

**Expected:**
- Fetches fresh data from `/hud-data` endpoint
- Shows default weather for Jakarta

---

## Verification Checklist

Open browser DevTools (F12) to verify:

### Backend Logs
```
✅ INFO - Executing function: get_weather
✅ INFO - Processing HUD data for tool: get_weather
✅ INFO - Generated final response with function results
```

### Frontend Console
```
✅ Received response: {response, base64_audio, hud_sections}
✅ Updating HUD with tool data: [Array(3)]
✅ Rendering HUD data directly: {sections: Array(3)}
```

### Network Tab
```
✅ POST http://localhost:8000/generate
   Response: {
     "response": "The weather in Jakarta...",
     "base64_audio": "UklGRi...",
     "hud_sections": [...]
   }
```

---

## Troubleshooting

### Issue: HUD doesn't appear

**Check:**
```javascript
// In browser console
console.log(window.auraHUD);  // Should be defined
```

**Fix:**
- Ensure `hud.js` is loaded in `index.html`
- Check for JavaScript errors in console

---

### Issue: Empty HUD sections

**Check Backend:**
```python
# Did tools get called?
# Check backend logs for "Executing function:"
```

**Fix:**
- Ensure OpenWeatherMap API key is set in `config.yaml`
- Try a different query that triggers tools

---

### Issue: HUD shows but no data

**Check Response:**
```javascript
// In Network tab, look at /generate response
// Should have "hud_sections": [...]
```

**Fix:**
- Check Brain is returning dict, not string
- Verify `_process_tool_call_for_hud` is being called

---

## Success Indicators

✅ **Full Integration Working When:**

1. Weather query → HUD appears automatically
2. Multiple sections display correctly
3. Images load (weather icons)
4. Data is accurate and formatted
5. HUD closes when clicking X
6. Manual refresh works
7. Non-tool queries don't show HUD

---

## Example Session

```
User: "Hello AURA"
AI: "Good day, Sir! How may I assist you?"
HUD: (Hidden)

User: "What's the weather?"
AI: *calls get_weather("Jakarta")*
AI: "The weather in Jakarta is clear sky, 28°C..."
HUD: (Appears with 3 weather sections)

User: "What time is it?"
AI: *calls get_time()*
AI: "It's 10:15 AM WIB, Sir"
HUD: (Updates with time section)

User: "Thanks!"
AI: "You're welcome, Sir!"
HUD: (Stays visible with last data)
```

---

## Advanced Testing

### Test Tool Error Handling

1. Remove OpenWeather API key from config
2. Ask: "What's the weather?"
3. Expected: Error message in HUD

### Test HUD Dragging

1. Click and drag HUD header
2. Expected: HUD moves smoothly
3. Stays within viewport bounds

### Test HUD Persistence

1. Ask weather question → HUD appears
2. Ask normal question → HUD stays
3. Ask different weather → HUD updates

---

## Next: Real Usage

Once testing passes, try:

- Ask about weather in your city
- Check your calendar (if configured)
- Mix queries: "Weather in Paris and time?"
- See HUD update in real-time!

Happy testing! 🚀
