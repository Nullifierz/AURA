# OpenWeatherMap Integration Setup

## 1. Get Your API Key

If you don't have an OpenWeatherMap API key yet:

1. Go to [OpenWeatherMap](https://openweathermap.org/)
2. Sign up for a free account
3. Go to your API keys section
4. Copy your API key

## 2. Add API Key to Config

Open `settings/config.yaml` and replace the placeholder:

```yaml
api_keys:
  google_genai: "AIzaSyDeFZ7nye9kIPI-NPWyP6rr1urnIaOndKM"
  openweather: "YOUR_ACTUAL_API_KEY_HERE"  # Replace this!
```

## 3. Install Dependencies

```bash
pip install requests
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## 4. Test the Weather API

### Option 1: Test via Backend Endpoint

Start your backend:
```bash
python main.py
```

Then visit: `http://localhost:8000/hud-data?location=Jakarta`

### Option 2: Test in Python

```python
from core.tools import get_weather_data

# Get weather for Jakarta
weather = get_weather_data("Jakarta")
print(weather)

# Get weather for another city
weather = get_weather_data("Tokyo")
print(weather)
```

## 5. Use in HUD

The HUD will automatically fetch weather data when you open it. You can also specify a different location:

```javascript
// Load HUD with specific location
fetch('http://localhost:8000/hud-data?location=Tokyo')
  .then(r => r.json())
  .then(data => window.auraHUD.renderContent(data));
```

## Weather Data Included

The HUD will display:
- **Weather Overview:**
  - Location & Country
  - Current condition description
  - Temperature & "feels like"
  - Humidity
  - Wind speed
  - Visibility

- **Sun Times:**
  - Sunrise time
  - Sunset time
  - Atmospheric pressure
  - Cloud coverage

- **Weather Icon:**
  - Visual representation from OpenWeatherMap

## Supported Locations

You can query weather for:
- City names: `"Jakarta"`, `"London"`, `"New York"`
- City + Country: `"Jakarta,ID"`, `"London,UK"`
- Coordinates: Use lat/lon (requires API modification)

## API Rate Limits

Free tier includes:
- 1,000 API calls per day
- 60 calls per minute

The HUD caches data, so refreshing won't immediately hit the API again.

## Troubleshooting

### "Weather API not configured"
- Make sure you've added your API key to `config.yaml`
- Restart the backend after updating config

### "Location not found"
- Check the spelling of the city name
- Try adding country code: `"Jakarta,ID"`

### "Connection error"
- Check your internet connection
- Verify the API key is valid
- Check if OpenWeatherMap service is available

## Example Response

```json
{
  "sections": [
    {
      "title": "Weather - Jakarta, ID",
      "type": "keyvalue",
      "data": {
        "items": [
          {"key": "Condition", "value": "Partly Cloudy"},
          {"key": "Temperature", "value": "28.5°C"},
          {"key": "Feels Like", "value": "31.2°C"},
          {"key": "Humidity", "value": "75%"},
          {"key": "Wind Speed", "value": "3.5 m/s"},
          {"key": "Visibility", "value": "10 km"}
        ]
      }
    },
    {
      "title": "Sun Times",
      "type": "keyvalue",
      "data": {
        "items": [
          {"key": "Sunrise", "value": "05:45 AM"},
          {"key": "Sunset", "value": "06:15 PM"},
          {"key": "Pressure", "value": "1012 hPa"},
          {"key": "Cloudiness", "value": "40%"}
        ]
      }
    },
    {
      "title": "Current Conditions",
      "type": "image",
      "data": {
        "url": "https://openweathermap.org/img/wn/02d@2x.png",
        "caption": "Partly Cloudy"
      }
    }
  ]
}
```
