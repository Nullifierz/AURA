# 🎨 Custom Weather Icons Guide

## Current Setup

The HUD now displays the weather icon **at the top** with special featured styling:

- ✅ Image appears first (before other data)
- ✅ Larger display with prominent border
- ✅ Glowing cyan border effect
- ✅ Caption below the image
- ✅ Special background highlight

## Using Custom Images

### Option 1: Replace OpenWeatherMap Icons

Edit `core/brain.py` to use your custom images:

```python
# In _process_tool_call_for_hud method, weather section:

# Instead of OpenWeatherMap icon:
# icon_url = f"https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"

# Use your custom image:
icon_url = "/path/to/your/custom/weather-icon.png"

# Or map weather conditions to custom images:
custom_icons = {
    "clear sky": "images/sunny.png",
    "few clouds": "images/partly-cloudy.png",
    "scattered clouds": "images/cloudy.png",
    "broken clouds": "images/overcast.png",
    "shower rain": "images/rain.png",
    "rain": "images/rain-heavy.png",
    "thunderstorm": "images/storm.png",
    "snow": "images/snow.png",
    "mist": "images/fog.png"
}

condition = weather_data['description'].lower()
icon_url = custom_icons.get(condition, "images/default.png")
```

### Option 2: Create Weather Image Folder

1. **Create image folder:**
   ```
   d:\Personal\Hobi\AURA\frontend\images\weather\
   ```

2. **Add your custom images:**
   ```
   weather/
   ├── sunny.png
   ├── cloudy.png
   ├── overcast.png
   ├── rain.png
   ├── storm.png
   ├── snow.png
   └── fog.png
   ```

3. **Update Brain to use local images:**

```python
# In core/brain.py, _process_tool_call_for_hud:

def _get_custom_weather_icon(condition, icon_code):
    """Map weather condition to custom icon."""
    
    # Map OpenWeatherMap codes to custom images
    icon_map = {
        '01d': 'sunny.png',      # clear sky day
        '01n': 'clear-night.png', # clear sky night
        '02d': 'partly-cloudy.png',
        '02n': 'partly-cloudy-night.png',
        '03d': 'cloudy.png',
        '03n': 'cloudy.png',
        '04d': 'overcast.png',
        '04n': 'overcast.png',
        '09d': 'rain.png',
        '09n': 'rain.png',
        '10d': 'rain-light.png',
        '10n': 'rain-light.png',
        '11d': 'storm.png',
        '11n': 'storm.png',
        '13d': 'snow.png',
        '13n': 'snow.png',
        '50d': 'fog.png',
        '50n': 'fog.png'
    }
    
    filename = icon_map.get(icon_code, 'default.png')
    return f"images/weather/{filename}"

# Then use it:
icon_url = _get_custom_weather_icon(
    weather_data['description'],
    weather_data['icon']
)
```

### Option 3: Animated SVG Icons

For even better visuals, use animated SVG:

```python
# Animated weather SVGs
icon_url = "images/weather/animated-rain.svg"

# Or use a library like:
# https://github.com/basmilius/weather-icons
# https://erikflowers.github.io/weather-icons/
```

## Recommended Image Specifications

### Size:
- **Minimum:** 200x200px
- **Recommended:** 400x400px
- **Maximum:** 800x800px (for retina displays)

### Format:
- **PNG:** Best for static icons with transparency
- **SVG:** Best for scalable, crisp icons
- **WEBP:** Best for smaller file sizes

### Style:
- **Transparent background** (works best with HUD)
- **Cyan/blue color palette** (matches HUD theme)
- **Simple, clear iconography**
- **Glowing effects optional** (HUD adds its own glow)

## Creating Your Own Weather Icons

### Design Tips:

1. **Color Palette:**
   ```css
   Primary Cyan: #00FFFF
   Dark Cyan: #0096FF
   Light Cyan: #66FFFF
   Background: Transparent or rgba(0, 50, 100, 0.3)
   ```

2. **Icon Dimensions:**
   - Square aspect ratio (1:1)
   - Centered composition
   - Leave 10% padding on all sides

3. **Recommended Tools:**
   - **Figma** (free, web-based)
   - **Adobe Illustrator** (professional)
   - **Inkscape** (free, open-source)
   - **Canva** (easy, templates available)

### Example Implementation:

```python
# core/brain.py - Enhanced custom icons

def _process_tool_call_for_hud(self, tool_name: str, tool_args: dict, tool_result: str):
    if tool_name == "get_weather":
        location = tool_args.get("location", "Unknown")
        try:
            from core.tools.weather_tool import get_weather_data
            
            weather_data = get_weather_data(location)
            
            if "error" not in weather_data:
                # Use custom weather icon
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
                # ... rest of sections
                
def _get_weather_icon_url(self, weather_data):
    """Get custom weather icon URL based on conditions."""
    
    # Option 1: Use your custom images
    condition = weather_data['description'].lower()
    
    if "clear" in condition:
        return "images/weather/sunny.png"
    elif "cloud" in condition:
        if "few" in condition:
            return "images/weather/partly-cloudy.png"
        else:
            return "images/weather/cloudy.png"
    elif "rain" in condition or "drizzle" in condition:
        return "images/weather/rain.png"
    elif "thunder" in condition or "storm" in condition:
        return "images/weather/storm.png"
    elif "snow" in condition:
        return "images/weather/snow.png"
    elif "mist" in condition or "fog" in condition:
        return "images/weather/fog.png"
    else:
        # Fallback to OpenWeatherMap
        return f"https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"
```

## CSS Customization

To further customize the image display:

```css
/* In frontend/css/style.css */

/* Make image larger */
.hud-image {
    max-width: 350px;  /* Increase from 300px */
    padding: 20px;     /* More padding */
}

/* Add animation */
.hud-image {
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* Add stronger glow for custom images */
.hud-section-featured .hud-image {
    box-shadow: 
        0 0 20px rgba(0, 255, 255, 0.4),
        0 0 40px rgba(0, 255, 255, 0.2);
}

/* Make image fill more space */
.hud-image-container {
    padding: 15px 0;
}
```

## Testing Custom Icons

1. **Place your image:**
   ```
   d:\Personal\Hobi\AURA\frontend\images\weather\sunny.png
   ```

2. **Update Brain.py:**
   ```python
   icon_url = "images/weather/sunny.png"
   ```

3. **Test:**
   ```
   Ask: "What's the weather?"
   ```

4. **Verify:**
   - Image appears at top
   - Has cyan border glow
   - Caption displays below
   - Loads without errors

## Free Weather Icon Resources

- **Meteocons:** https://bas.dev/work/meteocons (Animated, free)
- **Weather Icons:** https://erikflowers.github.io/weather-icons/
- **Iconify:** https://iconify.design/icon-sets/wi/
- **Flaticon:** https://www.flaticon.com/packs/weather
- **Icons8:** https://icons8.com/icons/set/weather

## Next Steps

1. Download or create your weather icons
2. Save them to `frontend/images/weather/`
3. Update `core/brain.py` with custom icon mapping
4. Test with different weather conditions
5. Adjust CSS styling to your preference

The HUD is now optimized to showcase your custom weather images beautifully! 🎨
