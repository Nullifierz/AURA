# 💡 Smart Light Control - AURA Integration

**Feature Added**: October 26, 2025  
**Technology**: WiZ Smart Lights via pywizlight library

---

## 🎯 Overview

AURA can now control WiZ smart lights in your home! You can turn lights on/off, adjust brightness, change colors, set scenes, and more - all with voice commands.

---

## ✨ Features

### **Basic Control**
- ✅ Turn lights on/off
- ✅ Adjust brightness (0-255)
- ✅ Check light status

### **Color Control**
- ✅ Set RGB colors (millions of colors)
- ✅ Set color temperature (warm to cool white)
- ✅ Preset color scenes

### **Scenes** (35 built-in scenes)
- Party 🎉
- Focus 💼
- Relax 🧘
- Bedtime 🌙
- Romance 💕
- Sunset 🌅
- Ocean 🌊
- Christmas 🎄
- And 27 more!

### **Discovery**
- ✅ Auto-discover all lights in network
- ✅ Multi-light support (coming soon)

---

## 🎮 Voice Commands

### **Basic Commands**
```
"Turn on the lights"
"Turn off the lights"
"What's the light status?"
"Is the light on?"
```

### **Brightness**
```
"Set brightness to 50%"
"Make it brighter"
"Dim the lights"
"Maximum brightness"
"Set brightness to 128"  (0-255 scale)
```

### **Colors**
```
"Make the light red"
"Change to blue"
"Set color to purple"
"Make it warm white"
"Change to cool white"
```

### **Scenes**
```
"Party mode"
"Focus mode"
"Relaxing mode"
"Bedtime mode"
"Romantic lighting"
"Sunset scene"
"Ocean scene"
```

---

## 🛠️ Configuration

### **1. Find Your Light's IP Address**

```bash
# Method 1: Use pywizlight CLI
python -m pywizlight.cli discover

# Method 2: Check your router's connected devices
# Look for "WiZ" or "Wiz" devices
```

### **2. Update Default IP** (Optional)

Edit `core/tools/light_tool.py`:

```python
class LightController:
    def __init__(self):
        self.lights: Dict[str, wizlight] = {}
        self.default_ip = "192.168.0.102"  # ← Change this to your light's IP
```

### **3. Multiple Lights** (Optional)

```python
# In your code or via API
from core.tools import light_controller

light_controller.add_light("bedroom", "192.168.0.102")
light_controller.add_light("living_room", "192.168.0.103")
light_controller.add_light("kitchen", "192.168.0.104")
```

---

## 📚 API Reference

### **Functions Available**

#### `turn_on_light(light_name=None, brightness=None, rgb=None, color_temp=None, scene=None)`
Turn on a light with optional parameters.

**Parameters**:
- `light_name` (str, optional): Name of the light
- `brightness` (int, optional): 0-255
- `rgb` (str, optional): "r,g,b" format (e.g., "255,0,0")
- `color_temp` (int, optional): 2200-6500 Kelvin
- `scene` (int, optional): Scene ID 1-35

**Examples**:
```python
# Turn on at 50% brightness
turn_on_light(brightness=128)

# Turn on red
turn_on_light(rgb="255,0,0")

# Turn on warm white
turn_on_light(color_temp=2700)

# Party scene
turn_on_light(scene=4)
```

#### `turn_off_light(light_name=None)`
Turn off a light.

#### `get_light_state(light_name=None)`
Get current light status.

**Returns**:
```json
{
    "success": true,
    "light": "default",
    "state": "on",
    "brightness": 128,
    "rgb": [255, 0, 0],
    "color_temp": 3000
}
```

#### `set_brightness(brightness, light_name=None)`
Set brightness (0-255).

#### `set_color(r, g, b, light_name=None)`
Set RGB color (0-255 each).

#### `set_scene(scene_id, light_name=None)`
Set a predefined scene (1-35).

#### `discover_lights(broadcast="192.168.0.255")`
Discover all lights in network.

---

## 🎨 Available Scenes

| ID | Scene Name | Description |
|----|-----------|-------------|
| 1 | Ocean | Blue/teal waves |
| 2 | Romance | Soft pink/red |
| 3 | Sunset | Orange/red gradient |
| 4 | Party | Rainbow colors |
| 5 | Fireplace | Warm orange flicker |
| 6 | Cozy | Warm white |
| 7 | Forest | Green tones |
| 8 | Pastel Colors | Soft colors |
| 9 | Wake up | Gradual brightness |
| 10 | Bedtime | Dim warm |
| 11 | Warm White | 2700K |
| 12 | Daylight | 4000K |
| 13 | Cool White | 6500K |
| 14 | Night Light | Very dim |
| 15 | Focus | Bright cool |
| 16 | Relax | Dim warm |
| 17 | True Colors | Full RGB |
| 18 | TV Time | Dim cool |
| 19 | Plant Growth | Purple grow |
| 20 | Spring | Light green |
| 21 | Summer | Bright yellow |
| 22 | Fall | Orange/brown |
| 23 | Deep Dive | Dark blue |
| 24 | Jungle | Green/yellow |
| 25 | Mojito | Lime green |
| 26 | Club | Pulsing colors |
| 27 | Christmas | Red/green |
| 28 | Halloween | Orange/purple |
| 29 | Candlelight | Flicker warm |
| 30 | Golden White | Soft gold |
| 31 | Pulse | Breathing effect |
| 32 | Steampunk | Bronze tones |
| 33 | Rhythm | Music sync |
| 34 | Diwali | Festival colors |
| 35 | Snowy Sky | Cool blue |

---

## 🔧 Technical Details

### **Library**: pywizlight v0.6.3
- **Protocol**: UDP broadcast
- **Port**: 38899 (default)
- **Response Time**: < 100ms
- **Async**: Full asyncio support

### **Features Supported**:
- ✅ On/Off control
- ✅ Brightness (0-255)
- ✅ RGB colors (16M colors)
- ✅ Color temperature (2200-6500K)
- ✅ White channels (warm/cold)
- ✅ 35 preset scenes
- ✅ State queries
- ✅ Discovery

### **Compatible Devices**:
- WiZ Smart Bulbs (all models)
- WiZ Smart Plugs
- WiZ Smart Strips
- Philips WiZ Connected bulbs

---

## 🧪 Testing

Test file: `tests/test_light.py`

```python
import asyncio
from pywizlight import wizlight, PilotBuilder

async def main():
    light = wizlight("192.168.0.102")
    
    # Turn on with cool white
    await light.turn_on(PilotBuilder(cold_white=255))
    
    print("Light turned on!")

if __name__ == "__main__":
    asyncio.run(main())
```

Run test:
```bash
cd tests
python test_light.py
```

---

## 📊 Tool Integration Status

| Tool | Status | Count |
|------|--------|-------|
| Calendar | ✅ Active | 1 |
| Weather | ✅ Active | 1 |
| Time/Date | ✅ Active | 2 |
| Search | ✅ Active | 1 |
| **Smart Light** | **✅ Active** | **7** |
| To-Do | ✅ Active | 6 |
| **Total** | **18 tools** | |

---

## 🚀 Example Workflows

### **Morning Routine**
```
You: "Good morning AURA"
AURA: "Good morning, Sir."

You: "Turn on the lights"
AURA: "Lights turned on, Sir."

You: "Set to daylight mode"
AURA: "Daylight scene activated, Sir."
```

### **Evening Relaxation**
```
You: "AURA, it's evening"
AURA: "Good evening, Sir."

You: "Set relaxing mood"
AURA: "Relax scene activated, Sir."

You: "Lower brightness to 30%"
AURA: "Brightness set to 30%, Sir."
```

### **Party Time**
```
You: "AURA, party mode"
AURA: "Party scene activated, Sir. Let's celebrate!"
```

### **Bedtime**
```
You: "AURA, I'm going to bed"
AURA: "Goodnight, Sir."

You: "Bedtime mode"
AURA: "Bedtime scene activated. Sweet dreams, Sir."

You: "Turn off lights in 5 minutes"
AURA: "Reminder set for 5 minutes, Sir."
```

---

## 🐛 Troubleshooting

### **Light Not Responding**
1. Check if light is on the same network
2. Verify IP address is correct
3. Try pinging the light: `ping 192.168.0.102`
4. Restart the light (power cycle)

### **Discovery Not Finding Lights**
1. Check broadcast address matches your network
2. Disable VPN if active
3. Check firewall settings (UDP port 38899)
4. Ensure lights are powered on

### **Connection Timeout**
1. Check network latency
2. Move router closer to lights
3. Reduce number of simultaneous commands
4. Check WiFi signal strength

---

## 🔮 Future Enhancements

### **Planned Features**:
- [ ] Multi-light group control
- [ ] Custom scene creation
- [ ] Schedule automation
- [ ] Brightness animation/fading
- [ ] Music sync mode
- [ ] Location-based automation
- [ ] Energy monitoring
- [ ] Voice-activated presets

---

## 📝 Notes

- Light commands are asynchronous for best performance
- Multiple commands in quick succession are queued
- State is cached for 5 seconds to reduce network traffic
- All commands have timeout protection (default 10s)

---

## 🎉 Success!

Your AURA AI assistant can now control your smart lights! Try it out:

```
"AURA, turn on the lights"
"AURA, make it purple"
"AURA, party mode!"
```

**Welcome to the future of smart home control!** 🏠✨

---

**Documentation Version**: 1.0  
**Last Updated**: October 26, 2025  
**Author**: AURA Development Team
