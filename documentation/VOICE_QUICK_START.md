# 🚀 Voice Input - Quick Start Guide

Get AURA's voice input running in **5 minutes**!

---

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project
cd d:\Personal\Hobi\AURA

# Install new packages
pip install faster-whisper webrtcvad python-Levenshtein websockets numpy

# OR if using uv
uv pip install -e .
```

---

## Step 2: Test Voice System (1 minute)

```bash
# Test the ears module
python core/ears.py
```

**Expected output:**
```
Initializing AURA Ears (Voice Input System)
Loading faster-whisper model: small.en on cpu
Whisper model loaded successfully
✅ Voice input system started (State: standby)
💡 Say one of these to wake: aura, aurora, jarvis
```

**Try it:**
1. Say: **"AURA"**
2. You should see: `✅ Wake word detected`
3. Say a command: **"Hello"**
4. Say: **"That would be all"**
5. Press Ctrl+C to stop

If this works, you're ready!

---

## Step 3: Start AURA (1 minute)

```bash
# Start the backend
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 4: Open Frontend (30 seconds)

Open your browser:
```
http://localhost:8000/frontend/index.html
```

You should see:
- AURA visualization
- Text input box
- **NEW**: Microphone button (cyan circle)
- **NEW**: Voice status indicator (top-left)

---

## Step 5: Enable Voice (30 seconds)

1. **Click the microphone button** (bottom center)
2. Status indicator changes to **"Connecting..."** (orange)
3. Then **"Standby (say wake word)"** (gray)
4. Browser may ask for mic permission - click **Allow**

---

## Step 6: Test It! 🎉

### First Command:
1. Say: **"AURA"** clearly
2. Status changes to **"Listening..."** (cyan, pulsing)
3. Say: **"What's the weather?"**
4. Watch AURA:
   - Transcription appears
   - Processing indicator (yellow)
   - Response + audio (green)
   - HUD windows pop up with weather data

### Return to Standby:
5. Say: **"That would be all"**
6. Status returns to **"Standby"** (gray)

---

## 🎯 Quick Commands to Try

```
"AURA" → "Turn on the lights"
"AURA" → "Add task buy groceries tomorrow"
"AURA" → "What time is it?"
"AURA" → "Search for Python tutorials"
"AURA" → "Show my calendar"
```

Always end with: **"That would be all"** or **"Mute"**

---

## 🐛 Quick Troubleshooting

### Wake word not detected?
- Speak louder or closer to mic
- Try: **"Hey AURA"** or **"Aurora"**
- Check config: Lower `similarity_threshold` to 0.5

### Mic not working?
- Check browser permissions (🔒 in address bar)
- Try different browser (Chrome recommended)
- Test system mic in Windows Sound Settings

### WebSocket won't connect?
- Restart backend (`python main.py`)
- Check console for errors (F12)
- Ensure port 8000 is not blocked

### Too slow?
- Change model in `config.yaml`:
  ```yaml
  whisper:
    model_size: "base.en"  # Faster but less accurate
  ```

---

## ⚙️ Quick Settings

### Make Wake Word More Sensitive
`config.yaml`:
```yaml
wake_word:
  similarity_threshold: 0.5  # Default: 0.65
```

### Change Wake Word
```yaml
wake_word:
  primary_words: ["jarvis", "computer"]
```

### Longer Listening Time
```yaml
wake_word:
  auto_mute_timeout: 60  # Default: 30 seconds
```

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] `python core/ears.py` works
- [ ] Backend running on port 8000
- [ ] Frontend loaded in browser
- [ ] Mic permission granted
- [ ] Voice button clicked (status shows)
- [ ] Wake word "AURA" triggers listening
- [ ] Commands are transcribed
- [ ] AURA responds with voice
- [ ] "That would be all" returns to standby

---

## 🎊 You're Done!

Your AURA is now **fully hands-free**! 

No keyboard, no mouse, just voice.

**Next:** Check out `VOICE_INPUT_COMPLETE.md` for advanced features.

---

## 💬 Need Help?

Check the logs:
```bash
tail -f logs/aura_*.log
```

Enable debug mode:
```yaml
# config.yaml
system:
  log_level: "DEBUG"
```

Test individual components:
```bash
python core/ears.py          # Test voice input
python tests/test_tools.py   # Test tools
```

---

**That's it! Enjoy your voice-controlled AURA! 🎤✨**
