# 🎤 AURA Voice Input System

**Hands-free voice control with wake word detection and real-time communication**

---

## Quick Links

- 📖 [Complete Documentation](VOICE_INPUT_COMPLETE.md)
- 🚀 [5-Minute Quick Start](VOICE_QUICK_START.md)
- 📋 [Implementation Summary](VOICE_IMPLEMENTATION_SUMMARY.md)

---

## Features

- ✅ **Wake Word Detection** - Say "AURA" to activate (with fuzzy matching)
- ✅ **Fuzzy Matching** - Handles mishears like "Ora", "Oda", "Aurora"
- ✅ **Real-time WebSocket** - Instant bidirectional communication
- ✅ **Voice Activity Detection** - Efficient speech processing
- ✅ **Multiple States** - Standby, Listening, Processing, Speaking
- ✅ **Visual Feedback** - Color-coded status indicator
- ✅ **Auto-mute** - Configurable timeout
- ✅ **Hands-free** - No keyboard or mouse needed

---

## Installation

```bash
pip install faster-whisper webrtcvad python-Levenshtein websockets numpy
```

---

## Usage

### 1. Start Backend
```bash
python main.py
```

### 2. Open Frontend
```
http://localhost:8000/frontend/index.html
```

### 3. Enable Voice
Click the microphone button (bottom center)

### 4. Talk to AURA
```
"AURA" → "What's the weather?" → "That would be all"
```

---

## Configuration

Edit `settings/config.yaml`:

```yaml
wake_word:
  primary_words: ["aura", "aurora"]
  similarity_threshold: 0.65
  mute_phrases: ["that would be all", "mute"]
  auto_mute_timeout: 30
```

---

## Architecture

```
Microphone → VAD → Whisper → Fuzzy Match → Brain → TTS → Speaker
                                ↓
                          WebSocket ←→ Frontend
```

---

## Problem Solved

**Before**: Whisper transcribes "AURA" as "Ora", "Oda", "All Right"  
**After**: Fuzzy matching catches all variations automatically

---

## Documentation

| Document | Purpose |
|----------|---------|
| **VOICE_QUICK_START.md** | Get started in 5 minutes |
| **VOICE_INPUT_COMPLETE.md** | Full documentation |
| **VOICE_IMPLEMENTATION_SUMMARY.md** | Technical deep dive |

---

## Status

✅ **COMPLETE & READY TO USE**

---

## Support

Check logs for debugging:
```bash
tail -f logs/aura_*.log
```

Test components:
```bash
python core/ears.py  # Test voice input
```

---

*Built with ❤️ by Nullifierz | November 2025*
