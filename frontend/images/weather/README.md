# Weather Images Folder

Place your custom weather icons here.

## Recommended Structure:

```
weather/
├── sunny.png           (Clear sky, day)
├── clear-night.png     (Clear sky, night)
├── partly-cloudy.png   (Few clouds, day)
├── cloudy.png          (Scattered/broken clouds)
├── overcast.png        (Overcast)
├── rain.png            (Rain/showers)
├── rain-light.png      (Light rain/drizzle)
├── storm.png           (Thunderstorm)
├── snow.png            (Snow)
├── fog.png             (Mist/fog)
└── default.png         (Fallback)
```

## Image Specifications:

- **Size:** 400x400px recommended
- **Format:** PNG with transparency
- **Color:** Cyan/blue palette to match HUD
- **Style:** Simple, clear icons

## Quick Start:

1. Download free weather icons from:
   - https://bas.dev/work/meteocons
   - https://erikflowers.github.io/weather-icons/
   - https://icons8.com/icons/set/weather

2. Save them to this folder

3. Update `core/brain.py` to use custom icons (see CUSTOM_WEATHER_ICONS.md)

## Current Setup:

Currently using OpenWeatherMap icons from:
`https://openweathermap.org/img/wn/{icon_code}@2x.png`

These will be replaced when you add custom images and update the Brain code.
