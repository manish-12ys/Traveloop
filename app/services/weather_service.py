"""
Weather Service for Phase 5
Handles interactions with OpenWeatherMap API.
"""

import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory cache: {(lat, lon): {'data': [...], 'timestamp': datetime}}
_WEATHER_CACHE = {}
CACHE_EXPIRY_SECONDS = 3600 # 1 hour

class WeatherService:
    @staticmethod
    def _get_api_key():
        return os.getenv('OPENWEATHERMAP_API_KEY')

    @staticmethod
    def get_forecast(lat, lon):
        """Fetch 5-day / 3-hour forecast for given coordinates"""
        # Cache key: round to 2 decimals (~1.1km precision) to increase hits
        key = (round(float(lat), 2), round(float(lon), 2))
        
        if key in _WEATHER_CACHE:
            cached = _WEATHER_CACHE[key]
            age = (datetime.now() - cached['timestamp']).total_seconds()
            if age < CACHE_EXPIRY_SECONDS:
                logger.info(f"Returning cached weather for {key}")
                return cached['data']

        api_key = WeatherService._get_api_key()
        if not api_key or api_key == 'your-openweathermap-api-key':
            logger.warning("OpenWeatherMap API Key missing, using mock data")
            return WeatherService._mock_forecast()

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data.get('list', []):
                forecasts.append({
                    'dt': item['dt'],
                    'temp': item['main']['temp'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'time': item['dt_txt']
                })
            
            # Update cache
            _WEATHER_CACHE[key] = {
                'data': forecasts,
                'timestamp': datetime.now()
            }
            return forecasts
        except Exception as e:
            logger.error(f"OpenWeatherMap Error: {e}")
            return WeatherService._mock_forecast()

    @staticmethod
    def _mock_forecast():
        """Returns generic mock weather data"""
        return [
            {'dt': 1715342400, 'temp': 22.5, 'description': 'clear sky', 'icon': '01d', 'time': '2026-05-10 12:00:00'},
            {'dt': 1715353200, 'temp': 24.2, 'description': 'few clouds', 'icon': '02d', 'time': '2026-05-10 15:00:00'},
            {'dt': 1715364000, 'temp': 21.0, 'description': 'scattered clouds', 'icon': '03n', 'time': '2026-05-10 18:00:00'},
            {'dt': 1715374800, 'temp': 18.5, 'description': 'broken clouds', 'icon': '04n', 'time': '2026-05-10 21:00:00'},
        ]
