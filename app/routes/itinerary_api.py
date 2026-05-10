"""
Itinerary API routes - Phase 5
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.trip_service import TripService
from app.services.weather_service import WeatherService
from app.services.routing_service import RoutingService
from app.models.stop import Stop

itinerary_bp = Blueprint('itinerary', __name__, url_prefix='/api/itinerary')

@itinerary_bp.route('/<int:trip_id>/weather', methods=['GET'])
@login_required
def get_trip_weather(trip_id):
    stops = TripService.get_trip_stops(trip_id, current_user.id)
    if not stops and trip_id > 0: # Check if empty due to unauthorized
        # Verify if trip exists but unauthorized
        from app.models.trip import Trip
        trip = Trip.query.get(trip_id)
        if trip and trip.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
    weather_data = {}
    for stop in stops:
        if stop.get('latitude') and stop.get('longitude'):
            forecast = WeatherService.get_forecast(stop['latitude'], stop['longitude'])
            weather_data[stop['id']] = forecast
            
    return jsonify(weather_data), 200

@itinerary_bp.route('/<int:trip_id>/travel-times', methods=['GET'])
@login_required
def get_travel_times(trip_id):
    stops = TripService.get_trip_stops(trip_id, current_user.id)
    times = []
    
    for i in range(len(stops) - 1):
        origin = stops[i]
        dest = stops[i+1]
        
        if origin.get('latitude') and dest.get('latitude'):
            info = RoutingService.get_travel_duration(
                (origin['latitude'], origin['longitude']),
                (dest['latitude'], dest['longitude'])
            )
            times.append({
                'from_stop_id': origin['id'],
                'to_stop_id': dest['id'],
                'info': info
            })
            
    return jsonify(times), 200

@itinerary_bp.route('/<int:trip_id>/stats', methods=['GET'])
@login_required
def get_trip_stats(trip_id):
    budget = TripService.get_budget_summary(trip_id, current_user.id)
    packing = TripService.get_packing_stats(trip_id, current_user.id)
    
    return jsonify({
        'budget': budget,
        'packing': packing
    }), 200
