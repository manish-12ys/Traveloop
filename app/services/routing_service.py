"""
Routing Service for Phase 5
Handles interactions with OpenRouteService API.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

# In-memory cache: {((lat1, lon1), (lat2, lon2)): {'data': {...}, 'timestamp': datetime}}
_ROUTING_CACHE = {}
CACHE_EXPIRY_SECONDS = 86400 # 24 hours

class RoutingService:
    @staticmethod
    def _get_api_key():
        return os.getenv('OPENROUTESERVICE_API_KEY')

    @staticmethod
    def get_travel_duration(origin_coords, dest_coords, profile='driving-car'):
        """
        Calculate travel duration and distance between two points.
        coords: (lat, lon)
        """
        from datetime import datetime
        # Round to 3 decimals (~110m precision)
        key = (
            (round(float(origin_coords[0]), 3), round(float(origin_coords[1]), 3)),
            (round(float(dest_coords[0]), 3), round(float(dest_coords[1]), 3)),
            profile
        )

        if key in _ROUTING_CACHE:
            cached = _ROUTING_CACHE[key]
            age = (datetime.now() - cached['timestamp']).total_seconds()
            if age < CACHE_EXPIRY_SECONDS:
                logger.info(f"Returning cached route for {key}")
                return cached['data']

        api_key = RoutingService._get_api_key()
        if not api_key or api_key == 'your-openrouteservice-api-key':
            logger.warning("OpenRouteService API Key missing, using mock data")
            return RoutingService._mock_duration(origin_coords, dest_coords)

        url = f"https://api.openrouteservice.org/v2/directions/{profile}"
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': api_key,
            'Content-Type': 'application/json; charset=utf-8'
        }
        body = {
            "coordinates": [
                [origin_coords[1], origin_coords[0]],
                [dest_coords[1], dest_coords[0]]
            ]
        }

        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            summary = data['routes'][0]['summary']
            result = {
                'distance': summary['distance'], # meters
                'duration': summary['duration'], # seconds
                'formatted_duration': RoutingService._format_duration(summary['duration'])
            }
            
            # Update cache
            _ROUTING_CACHE[key] = {
                'data': result,
                'timestamp': datetime.now()
            }
            return result
        except Exception as e:
            logger.error(f"OpenRouteService Error: {e}")
            return RoutingService._mock_duration(origin_coords, dest_coords)

    @staticmethod
    def _format_duration(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    @staticmethod
    def _mock_duration(origin, dest):
        # Very rough estimation for mock data
        return {
            'distance': 50000,
            'duration': 3600,
            'formatted_duration': "1h 0m"
        }
