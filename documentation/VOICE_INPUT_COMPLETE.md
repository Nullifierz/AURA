# 🎤 Voice Input with Wake Word Detection - Implementation Complete!

## ✅ What Was Built

A **complete hands-free voice interaction system** for AURA using:
- **faster-whisper** for accurate speech-to-text
- **Fuzzy wake word matching** to handle variations ("AURA", "Aurora", "Ora", "Oda")
- **WebRTC VAD** for voice activity detection
- **WebSocket** real-time communication
- **State machine** for proper listening management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ Voice Button │ ───▶ │ VoiceClient  │ ◀───WebSocket────┐ │
│  └──────────────┘      └──────────────┘                   │ │
│         │                     │                            │ │
│         ▼                     ▼                            │ │
│  ┌──────────────┐      ┌──────────────┐                   │ │
│  │ Status       │      │ Audio Player │                   │ │
│  │ Indicator    │      └──────────────┘                   │ │
│  └──────────────┘                                          │ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                        BACKEND                               │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   FastAPI    │ ───▶ │ VoiceWS      │                    │
│  │   /ws/voice  │      │ Manager      │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                              │
│                               ▼                              │
│  ┌──────────────────────────────────────────────┐          │
│  │              EARS (Voice Input)              │          │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │          │
│  │  │ PyAudio  │→ │   VAD    │→ │ Whisper  │  │          │
│  │  │(Capture) │  │(Detect)  │  │(Transcr.)│  │          │
│  │  └──────────┘  └──────────┘  └──────────┘  │          │
│  │        │              │              │       │          │
│  │        └──────────────┴──────────────┘       │          │
│  │                      │                       │          │
│  │                      ▼                       │          │
│  │            ┌──────────────────┐              │          │
│  │            │  Wake Word Match │              │          │
│  │            │   (Fuzzy Logic)  │              │          │
│  │            └──────────────────┘              │          │
│  └──────────────────┬───────────────────────────┘          │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    Brain     │  │    Mouth     │  │     HUD      │    │
│  │  (Gemini AI) │  │   (Piper)    │  │  (Display)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 State Machine

```
┌──────────┐  Wake Word   ┌───────────┐  Command    ┌────────────┐
│ STANDBY  │─────────────▶│ LISTENING │────────────▶│ PROCESSING │
│          │◀─────────────│           │             │            │
└──────────┘  Mute/Timeout└───────────┘             └─────┬──────┘
     ▲                                                     │
     │                                                     │
     │                     ┌───────────┐                  │
     └─────────────────────│ SPEAKING  │◀─────────────────┘
           Audio Finished  └───────────┘  Response Ready
```

### States:
- **STANDBY**: Waiting for wake word ("AURA", "Aurora", etc.)
- **LISTENING**: Actively listening for commands
- **PROCESSING**: Processing command with AI
- **SPEAKING**: AURA is speaking (ignores mic input)

---

## 📦 New Files Created

### Backend
1. **`core/ears.py`** (520 lines)
   - Main voice input system
   - VAD integration
   - Whisper transcription
   - Fuzzy wake word matching
   - State management

2. **`core/voice_websocket.py`** (200 lines)
   - WebSocket manager
   - Connects Ears ↔ Brain ↔ Mouth
   - Real-time message handling
   - Callbacks for events

### Frontend
3. **`frontend/js/voice_client.js`** (250 lines)
   - WebSocket client
   - Event handling
   - State tracking
   - Manual controls

4. **`frontend/css/voice.css`** (90 lines)
   - Voice status indicator
   - Voice button styling
   - State-based animations
   - Color coding

---

## 🎨 UI Components

### 1. Voice Status Indicator (Top-Left)
Visual feedback showing current state:
- 🔴 **Red** (pulsing fast): Error
- 🟠 **Orange**: Connecting
- ⚫ **Gray**: Standby (disabled)
- 🔵 **Cyan** (pulsing): Listening
- 🟡 **Yellow** (pulsing): Processing
- 🟢 **Green** (pulsing): Speaking

### 2. Voice Button (Center)
Click to toggle voice input on/off

---

## 🚀 Installation

### 1. Install Dependencies

```bash
# Install Python packages
pip install faster-whisper webrtcvad python-Levenshtein websockets numpy
```

Or using uv:
```bash
uv pip install -e .
```

### 2. Verify Installation

```bash
python core/ears.py
```

You should see:
```
Initializing AURA Ears (Voice Input System)
Loading faster-whisper model: small.en on cpu
Whisper model loaded successfully
VAD initialized with aggressiveness level 3
AURA Ears initialized successfully
```

---

## ⚙️ Configuration

All settings are in `settings/config.yaml`:

### Wake Word Settings
```yaml
wake_word:
  enabled: true
  # Primary wake words (fuzzy matched)
  primary_words: ["aura", "aurora", "jarvis"]
  # Variations that will be accepted
  acceptable_variations: ["ora", "oda", "arora", "auora", "ura"]
  # Similarity threshold (0.0-1.0, lower = more lenient)
  similarity_threshold: 0.65
  # Phrases to return to standby
  mute_phrases: ["that would be all", "that will be all", "mute"]
  # Auto-mute after 30 seconds of no activity
  auto_mute_timeout: 30
```

### VAD (Voice Activity Detection)
```yaml
vad:
  enabled: true
  aggressiveness: 3  # 0-3, higher = more strict
  silence_duration_ms: 900  # Silence before processing
  min_speech_duration_ms: 300  # Minimum speech length
```

### Whisper Settings
```yaml
whisper:
  model_size: "small.en"  # tiny, base, small, medium, large
  device: "cpu"  # cpu or cuda
  compute_type: "int8"  # int8 is fastest
```

---

## 🎯 Usage

### Start AURA with Voice
1. Start backend:
   ```bash
   python main.py
   ```

2. Open frontend:
   ```
   http://localhost:8000/frontend/index.html
   ```

3. Click the **microphone button** (center bottom)

4. Wait for status to show **"Standby (say wake word)"**

5. Say: **"AURA"** or **"Aurora"** or **"Hey AURA"**

6. Status changes to **"Listening..."** with cyan pulsing indicator

7. Give your command: **"What's the weather?"**

8. AURA processes and responds

9. Say: **"That would be all"** to return to standby

---

## 🎤 Wake Word Detection

### How It Works

1. **Continuous Listening**: Mic always on, but only processes wake word check
2. **Fuzzy Matching**: Uses Levenshtein distance to match variations
3. **Whitelist**: Pre-defined acceptable variations
4. **Similarity Threshold**: Configurable tolerance (default: 0.65)

### Why Fuzzy Matching?

Whisper might transcribe "AURA" as:
- ✅ "Aura" (exact)
- ✅ "Aurora" (close)
- ✅ "Ora" (acceptable)
- ✅ "Oda" (acceptable with fuzzy)
- ✅ "Auora" (typo, but fuzzy matches)
- ❌ "Hello" (too different)
- ❌ "Computer" (too different)

### Example Log:
```
🎤 Heard: 'ora what's the weather' (State: standby)
✅ Wake word detected (fuzzy): 'ora' matches 'aura' (distance: 1)
🔄 State: standby → listening
💬 COMMAND: what's the weather
```

---

## 🔧 Advanced Features

### 1. Manual Wake/Mute
```javascript
// From browser console
window.auraAPI.startVoice();  // Enable voice
voiceClient.manualWake();     // Wake without saying word
voiceClient.manualMute();     // Mute without saying phrase
```

### 2. Check Status
```javascript
window.auraAPI.getStatus();
// Returns:
// {
//   voiceEnabled: true,
//   voiceState: "listening",
//   isPlaying: false,
//   ...
// }
```

### 3. Custom Wake Words
Edit `config.yaml`:
```yaml
wake_word:
  primary_words: ["jarvis", "computer", "hey assistant"]
```

---

## 🐛 Troubleshooting

### Issue: Mic not working
**Solution**: Check browser permissions. Allow microphone access.

### Issue: Wake word not detected
**Solutions**:
1. Lower `similarity_threshold` in config (try 0.5)
2. Add your accent's variation to `acceptable_variations`
3. Check logs to see what Whisper transcribes
4. Speak closer to mic
5. Try saying the full phrase: "Hey AURA"

### Issue: Too sensitive (false wake ups)
**Solutions**:
1. Raise `similarity_threshold` (try 0.75)
2. Remove variations from `acceptable_variations`
3. Increase VAD `aggressiveness` level

### Issue: Slow transcription
**Solutions**:
1. Use smaller model: `tiny.en` or `base.en`
2. Use `int8` compute type (fastest)
3. Consider GPU: set `device: "cuda"`

### Issue: WebSocket disconnects
**Solution**: Check firewall. Ensure port 8000 is open.

---

## 📊 Performance

### Models Comparison:
| Model     | Speed  | Accuracy | RAM Usage | Recommended For |
|-----------|--------|----------|-----------|-----------------|
| tiny.en   | 32x RT | 74%      | ~1 GB     | Testing         |
| base.en   | 16x RT | 78%      | ~1 GB     | Fast response   |
| small.en  | 6x RT  | 83%      | ~2 GB     | **Default**     |
| medium.en | 2x RT  | 89%      | ~5 GB     | High accuracy   |
| large-v3  | 1x RT  | 95%      | ~10 GB    | GPU only        |

*RT = Real-time factor (6x means 1 second audio processes in 0.16 seconds)*

---

## 🎨 Customization

### Change Status Colors
Edit `frontend/css/voice.css`:
```css
.voice-status-indicator.state-listening {
  background: #ff00ff;  /* Purple instead of cyan */
  box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
}
```

### Add Custom Mute Phrase
Edit `config.yaml`:
```yaml
wake_word:
  mute_phrases: 
    - "that would be all"
    - "goodbye AURA"
    - "sleep now"
    - "shut up"  # Your custom phrase
```

### Change Auto-Mute Timeout
```yaml
wake_word:
  auto_mute_timeout: 60  # 60 seconds instead of 30
```

---

## 🧪 Testing

### Test Voice Input
```bash
cd d:\Personal\Hobi\AURA
python core/ears.py
```

Say "AURA" and then commands. Watch the console for transcription.

### Test WebSocket
```javascript
// In browser console
const vc = new VoiceClient();
vc.connect();
vc.onConnected = (msg) => console.log("Connected!", msg);
vc.onWake = (msg) => console.log("Wake!", msg);
```

---

## 📝 Next Steps

### ✅ Completed
- [x] Wake word detection with fuzzy matching
- [x] Real-time voice input via WebSocket
- [x] VAD for efficient processing
- [x] State machine for proper flow
- [x] Visual status indicators
- [x] Hands-free operation

### 🚀 Future Enhancements
- [ ] Multiple user profiles (learn voice patterns)
- [ ] Custom wake word training
- [ ] Background noise cancellation
- [ ] Voice command shortcuts (macros)
- [ ] Multi-language wake words
- [ ] Offline mode (local model caching)

---

## 💡 Tips & Tricks

### Optimal Setup
1. Use headphones to prevent echo/feedback
2. Position mic 6-12 inches from mouth
3. Speak clearly but naturally
4. Reduce background noise
5. Start with small.en model, upgrade if needed

### Power User Commands
```
"AURA" → "weather" → "that would be all"
"AURA" → "turn on the lights" → "that will be all"
"AURA" → "add task buy groceries tomorrow" → "mute"
```

### Debugging
Enable DEBUG logging in `config.yaml`:
```yaml
system:
  log_level: "DEBUG"
  debug_mode: true
```

Watch logs:
```bash
tail -f logs/aura_*.log
```

---

## 🎉 Success Criteria

You'll know it's working when:
1. ✅ Voice status indicator shows in top-left
2. ✅ Clicking mic button connects (orange → gray)
3. ✅ Saying "AURA" triggers listening (cyan pulsing)
4. ✅ Commands are transcribed correctly
5. ✅ AURA responds with voice + HUD
6. ✅ "That would be all" returns to standby
7. ✅ Fully hands-free operation

---

## 📚 Technical Details

### Fuzzy Matching Algorithm
```python
def _fuzzy_match_wake_word(self, text: str) -> bool:
    # Normalize: lowercase, remove punctuation
    # Split into words
    # For each word:
    #   Calculate Levenshtein distance to wake words
    #   If distance <= threshold: MATCH
    # Return: match found or not
```

### VAD Processing
```python
# Check if audio chunk contains speech
if is_speech(chunk):
    speech_frames.append(chunk)
else:
    silence_frames += 1

# Process when enough silence detected
if silence >= 900ms:
    transcribe(speech_frames)
```

---

## 🏆 Credits

- **faster-whisper**: OpenAI Whisper optimized
- **webrtcvad**: Google WebRTC VAD
- **python-Levenshtein**: Edit distance calculation
- **FastAPI**: WebSocket backend
- **PyAudio**: Audio capture

---

**Author**: Nullifierz  
**Date**: November 1, 2025  
**Version**: 1.0  
**Project**: AURA AI Assistant

*"The future is voice-first. Now AURA is hands-free."* 🎤✨
