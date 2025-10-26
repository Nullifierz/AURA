# 🌦️ Weather Image Categories & Naming Guide

## OpenWeatherMap Weather Conditions

Based on the OpenWeatherMap API, here are **all possible weather conditions** and their icon codes.

## Complete Icon Code List

### ☀️ Clear Sky
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `01d` | Clear sky | Day | `clear-day.png` or `sunny.png` |
| `01n` | Clear sky | Night | `clear-night.png` |

### ☁️ Clouds
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `02d` | Few clouds (11-25%) | Day | `few-clouds-day.png` or `partly-cloudy.png` |
| `02n` | Few clouds | Night | `few-clouds-night.png` |
| `03d` | Scattered clouds (25-50%) | Day | `scattered-clouds.png` or `cloudy.png` |
| `03n` | Scattered clouds | Night | `scattered-clouds.png` |
| `04d` | Broken clouds (51-84%) | Day | `broken-clouds.png` or `overcast.png` |
| `04n` | Broken clouds | Night | `broken-clouds.png` |

### 🌧️ Rain
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `09d` | Shower rain | Day | `shower-rain.png` or `rain-heavy.png` |
| `09n` | Shower rain | Night | `shower-rain.png` |
| `10d` | Rain | Day | `rain-day.png` or `rain.png` |
| `10n` | Rain | Night | `rain-night.png` |

### ⛈️ Thunderstorm
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `11d` | Thunderstorm | Day | `thunderstorm.png` or `storm.png` |
| `11n` | Thunderstorm | Night | `thunderstorm.png` |

### ❄️ Snow
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `13d` | Snow | Day | `snow.png` |
| `13n` | Snow | Night | `snow.png` |

### 🌫️ Atmosphere
| Icon Code | Description | Time | Image Name Suggestion |
|-----------|-------------|------|----------------------|
| `50d` | Mist/Fog | Day | `mist.png` or `fog.png` |
| `50n` | Mist/Fog | Night | `mist.png` |

---

## Recommended Minimal Set (11 Images)

If you want to create a complete set, here are the essential images:

```
weather/
├── clear-day.png          (01d - sunny)
├── clear-night.png        (01n - clear night)
├── partly-cloudy.png      (02d, 02n - few clouds)
├── cloudy.png             (03d, 03n - scattered clouds)
├── overcast.png           (04d, 04n - broken clouds)
├── rain.png               (10d, 10n - rain)
├── rain-heavy.png         (09d, 09n - shower rain)
├── thunderstorm.png       (11d, 11n - storm)
├── snow.png               (13d, 13n - snow)
├── fog.png                (50d, 50n - mist/fog)
└── default.png            (fallback)
```

---

## Implementation Code

### Option 1: Simple Mapping (Day/Night Combined)

```python
# In core/brain.py

def _get_weather_icon_url(self, weather_data):
    """Map weather icon code to custom image."""
    
    icon_code = weather_data['icon']
    
    # Simple mapping (combine day/night)
    icon_map = {
        '01d': 'clear-day.png',
        '01n': 'clear-night.png',
        '02d': 'partly-cloudy.png',
        '02n': 'partly-cloudy.png',
        '03d': 'cloudy.png',
        '03n': 'cloudy.png',
        '04d': 'overcast.png',
        '04n': 'overcast.png',
        '09d': 'rain-heavy.png',
        '09n': 'rain-heavy.png',
        '10d': 'rain.png',
        '10n': 'rain.png',
        '11d': 'thunderstorm.png',
        '11n': 'thunderstorm.png',
        '13d': 'snow.png',
        '13n': 'snow.png',
        '50d': 'fog.png',
        '50n': 'fog.png',
    }
    
    filename = icon_map.get(icon_code, 'default.png')
    return f"images/weather/{filename}"
```

### Option 2: Descriptive Mapping (Text-Based)

```python
def _get_weather_icon_url(self, weather_data):
    """Map weather description to custom image."""
    
    description = weather_data['description'].lower()
    
    # Text-based mapping
    if 'clear' in description:
        return 'images/weather/sunny.png'
    elif 'few clouds' in description or 'partly' in description:
        return 'images/weather/partly-cloudy.png'
    elif 'scattered clouds' in description:
        return 'images/weather/cloudy.png'
    elif 'broken clouds' in description or 'overcast' in description:
        return 'images/weather/overcast.png'
    elif 'shower' in description:
        return 'images/weather/rain-heavy.png'
    elif 'rain' in description or 'drizzle' in description:
        return 'images/weather/rain.png'
    elif 'thunder' in description or 'storm' in description:
        return 'images/weather/thunderstorm.png'
    elif 'snow' in description:
        return 'images/weather/snow.png'
    elif 'mist' in description or 'fog' in description or 'haze' in description:
        return 'images/weather/fog.png'
    else:
        return 'images/weather/default.png'
```

---

## Weather Descriptions (Text Format)

The API also provides text descriptions. Here are all possible values:

### Group: Thunderstorm
- `thunderstorm with light rain`
- `thunderstorm with rain`
- `thunderstorm with heavy rain`
- `light thunderstorm`
- `thunderstorm`
- `heavy thunderstorm`
- `ragged thunderstorm`
- `thunderstorm with light drizzle`
- `thunderstorm with drizzle`
- `thunderstorm with heavy drizzle`

### Group: Drizzle
- `light intensity drizzle`
- `drizzle`
- `heavy intensity drizzle`
- `light intensity drizzle rain`
- `drizzle rain`
- `heavy intensity drizzle rain`
- `shower rain and drizzle`
- `heavy shower rain and drizzle`
- `shower drizzle`

### Group: Rain
- `light rain`
- `moderate rain`
- `heavy intensity rain`
- `very heavy rain`
- `extreme rain`
- `freezing rain`
- `light intensity shower rain`
- `shower rain`
- `heavy intensity shower rain`
- `ragged shower rain`

### Group: Snow
- `light snow`
- `snow`
- `heavy snow`
- `sleet`
- `light shower sleet`
- `shower sleet`
- `light rain and snow`
- `rain and snow`
- `light shower snow`
- `shower snow`
- `heavy shower snow`

### Group: Atmosphere
- `mist`
- `smoke`
- `haze`
- `sand/dust whirls`
- `fog`
- `sand`
- `dust`
- `volcanic ash`
- `squalls`
- `tornado`

### Group: Clear
- `clear sky`

### Group: Clouds
- `few clouds` (11-25%)
- `scattered clouds` (25-50%)
- `broken clouds` (51-84%)
- `overcast clouds` (85-100%)

---

## Quick Start File Names

Copy this list and create images with these exact names:

```
✅ Required (11 files):

clear-day.png
clear-night.png
partly-cloudy.png
cloudy.png
overcast.png
rain.png
rain-heavy.png
thunderstorm.png
snow.png
fog.png
default.png
```

```
📦 Optional (Extended set):

rain-light.png
drizzle.png
sleet.png
haze.png
smoke.png
tornado.png
dust.png
volcanic-ash.png
```

---

## Where to Find Free Icons

### 🎨 Recommended Resources:

1. **Meteocons** (Animated, Beautiful)
   - URL: https://bas.dev/work/meteocons
   - License: Free for personal/commercial
   - Format: SVG (animated)

2. **Weather Icons by Erik Flowers**
   - URL: https://erikflowers.github.io/weather-icons/
   - License: Free (OFL)
   - Format: Font/SVG

3. **Flaticon Weather Pack**
   - URL: https://www.flaticon.com/packs/weather-157
   - License: Free with attribution
   - Format: PNG/SVG

4. **Icons8 Weather**
   - URL: https://icons8.com/icons/set/weather
   - License: Free with link
   - Format: PNG/SVG

5. **Iconify**
   - URL: https://iconify.design/icon-sets/wi/
   - License: Various
   - Format: SVG

---

## Implementation in Brain

Update `core/brain.py` in the `_process_tool_call_for_hud` method:

```python
if "error" not in weather_data:
    # Get custom weather icon
    icon_url = self._get_weather_icon_url(weather_data)
    
    self.hud_sections.append({
        "title": "Current Conditions",
        "type": "image",
        "data": {
            "url": icon_url,
            "alt": weather_data['description'],
            "caption": weather_data['description']
        }
    })
```

Then add the helper method:

```python
def _get_weather_icon_url(self, weather_data):
    """Map weather icon code to custom image."""
    
    icon_code = weather_data['icon']
    
    icon_map = {
        '01d': 'clear-day.png',
        '01n': 'clear-night.png',
        '02d': 'partly-cloudy.png',
        '02n': 'partly-cloudy.png',
        '03d': 'cloudy.png',
        '03n': 'cloudy.png',
        '04d': 'overcast.png',
        '04n': 'overcast.png',
        '09d': 'rain-heavy.png',
        '09n': 'rain-heavy.png',
        '10d': 'rain.png',
        '10n': 'rain.png',
        '11d': 'thunderstorm.png',
        '11n': 'thunderstorm.png',
        '13d': 'snow.png',
        '13n': 'snow.png',
        '50d': 'fog.png',
        '50n': 'fog.png',
    }
    
    filename = icon_map.get(icon_code, 'default.png')
    return f"images/weather/{filename}"
```

---

## Testing Different Conditions

To test all your icons, ask about cities with different weather:

```
"What's the weather in London?"      → Often cloudy/rainy
"What's the weather in Dubai?"       → Often clear/sunny
"What's the weather in Moscow?"      → Might have snow
"What's the weather in Seattle?"     → Often rainy
"What's the weather in Singapore?"   → Often thunderstorms
```

---

Now you have the complete list! Create 11 images with those exact names and you'll have full coverage! 🎨
