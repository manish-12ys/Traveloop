"""Trip API routes - Phase 3"""

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.services.trip_service import TripService
from app.models.trip import Trip
from datetime import datetime

trip_api_bp = Blueprint('trip_api', __name__, url_prefix='/api/trips')

# Helper to verify trip ownership
def verify_trip_access(trip_id):
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    return trip is not None

# --- Stops ---
@trip_api_bp.route('/<int:trip_id>/stops', methods=['GET'])
@login_required
def get_stops(trip_id):
    return jsonify(TripService.get_trip_stops(trip_id, current_user.id)), 200

@trip_api_bp.route('/<int:trip_id>/stops', methods=['POST'])
@login_required
def add_stop(trip_id):
    data = request.get_json()
    try:
        arrival = datetime.fromisoformat(data['arrival_date']).date()
        departure = datetime.fromisoformat(data['departure_date']).date()
        stop = TripService.add_stop(
            trip_id, current_user.id, data['name'], data['location'], arrival, departure,
            latitude=data.get('latitude'), longitude=data.get('longitude')
        )
        if not stop: return {'error': 'Unauthorized or Not Found'}, 403
        return jsonify(stop), 201
    except (ValueError, KeyError) as e:
        return {'error': str(e)}, 400

@trip_api_bp.route('/<int:trip_id>/stops/<int:stop_id>', methods=['PUT'])
@login_required
def update_stop(trip_id, stop_id):
    data = request.get_json()
    if 'arrival_date' in data: data['arrival_date'] = datetime.fromisoformat(data['arrival_date']).date()
    if 'departure_date' in data: data['departure_date'] = datetime.fromisoformat(data['departure_date']).date()
    stop = TripService.update_stop(stop_id, trip_id, current_user.id, **data)
    if not stop: return {'error': 'Stop not found or Unauthorized'}, 404
    return jsonify(stop), 200

@trip_api_bp.route('/<int:trip_id>/stops/<int:stop_id>', methods=['DELETE'])
@login_required
def delete_stop(trip_id, stop_id):
    if TripService.delete_stop(stop_id, trip_id, current_user.id):
        return {'message': 'Stop deleted'}, 200
    return {'error': 'Stop not found or Unauthorized'}, 404

# --- Activities ---
@trip_api_bp.route('/<int:trip_id>/activities', methods=['GET'])
@login_required
def get_activities(trip_id):
    return jsonify(TripService.get_trip_activities(trip_id, current_user.id)), 200

@trip_api_bp.route('/<int:trip_id>/activities', methods=['POST'])
@login_required
def add_activity(trip_id):
    data = request.get_json()
    
    start_time = datetime.fromisoformat(data['start_time']) if data.get('start_time') else None
    end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
    
    activity = TripService.add_activity(
        trip_id=trip_id,
        user_id=current_user.id,
        title=data['title'],
        stop_id=data.get('stop_id'),
        description=data.get('description', ''),
        start_time=start_time,
        end_time=end_time,
        cost=float(data.get('cost', 0))
    )
    if not activity: return {'error': 'Unauthorized'}, 403
    return jsonify(activity), 201

@trip_api_bp.route('/<int:trip_id>/activities/<int:act_id>', methods=['PUT'])
@login_required
def update_activity(trip_id, act_id):
    data = request.get_json()
    if 'start_time' in data and data['start_time']: data['start_time'] = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data and data['end_time']: data['end_time'] = datetime.fromisoformat(data['end_time'])
    
    act = TripService.update_activity(act_id, trip_id, current_user.id, **data)
    if not act: return {'error': 'Activity not found or Unauthorized'}, 404
    return jsonify(act), 200

@trip_api_bp.route('/<int:trip_id>/activities/<int:act_id>', methods=['DELETE'])
@login_required
def delete_activity(trip_id, act_id):
    if TripService.delete_activity(act_id, trip_id, current_user.id):
        return {'message': 'Deleted'}, 200
    return {'error': 'Not found or Unauthorized'}, 404

@trip_api_bp.route('/<int:trip_id>/activities/reorder', methods=['PUT'])
@login_required
def reorder_activities(trip_id):
    data = request.get_json()
    activity_ids = data.get('activity_ids', [])
    if TripService.reorder_activities(trip_id, current_user.id, activity_ids):
        return {'message': 'Reordered'}, 200
    return {'error': 'Unauthorized'}, 403

# --- Budgets ---
@trip_api_bp.route('/<int:trip_id>/budget', methods=['GET'])
@login_required
def get_budget(trip_id):
    return jsonify(TripService.get_trip_budget_items(trip_id, current_user.id)), 200

@trip_api_bp.route('/<int:trip_id>/budget', methods=['POST'])
@login_required
def add_budget(trip_id):
    data = request.get_json()
    item = TripService.add_budget_item(
        trip_id, current_user.id, data['category'], data.get('description', ''),
        float(data.get('expected_amount', 0)), float(data.get('actual_amount', 0))
    )
    if not item: return {'error': 'Unauthorized'}, 403
    return jsonify(item), 201

@trip_api_bp.route('/<int:trip_id>/budget/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_budget(trip_id, item_id):
    if request.method == 'DELETE':
        success = TripService.delete_budget_item(item_id, trip_id, current_user.id)
        return ({'message': 'Deleted'}, 200) if success else ({'error': 'Not found or Unauthorized'}, 404)
    data = request.get_json()
    item = TripService.update_budget_item(item_id, trip_id, current_user.id, **data)
    return (jsonify(item), 200) if item else ({'error': 'Not found or Unauthorized'}, 404)

# --- Packing ---
@trip_api_bp.route('/<int:trip_id>/packing', methods=['GET', 'POST'])
@login_required
def manage_packing(trip_id):
    if request.method == 'GET':
        return jsonify(TripService.get_trip_packing_items(trip_id, current_user.id)), 200
    data = request.get_json()
    item = TripService.add_packing_item(trip_id, current_user.id, data['item_name'], data.get('category', 'General'))
    if not item: return {'error': 'Unauthorized'}, 403
    return jsonify(item), 201

@trip_api_bp.route('/<int:trip_id>/packing/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_packing(trip_id, item_id):
    if request.method == 'DELETE':
        success = TripService.delete_packing_item(item_id, trip_id, current_user.id)
        return ({'message': 'Deleted'}, 200) if success else ({'error': 'Not found or Unauthorized'}, 404)
    data = request.get_json()
    item = TripService.toggle_packing_item(item_id, trip_id, current_user.id, data.get('is_packed', False))
    return (jsonify(item), 200) if item else ({'error': 'Not found or Unauthorized'}, 404)

# --- Notes ---
@trip_api_bp.route('/<int:trip_id>/notes', methods=['GET', 'POST'])
@login_required
def manage_notes(trip_id):
    if request.method == 'GET':
        return jsonify(TripService.get_trip_notes(trip_id, current_user.id)), 200
    data = request.get_json()
    note = TripService.add_note(trip_id, current_user.id, data['content'], data.get('title', ''))
    if not note: return {'error': 'Unauthorized'}, 403
    return jsonify(note), 201

@trip_api_bp.route('/<int:trip_id>/notes/<int:note_id>', methods=['PUT', 'DELETE'])
@login_required
def modify_notes(trip_id, note_id):
    if request.method == 'DELETE':
        success = TripService.delete_note(note_id, trip_id, current_user.id)
        return ({'message': 'Deleted'}, 200) if success else ({'error': 'Not found or Unauthorized'}, 404)
    data = request.get_json()
    note = TripService.update_note(note_id, trip_id, current_user.id, data['content'], data.get('title'))
    return (jsonify(note), 200) if note else ({'error': 'Not found or Unauthorized'}, 404)

@trip_api_bp.route('/<int:trip_id>/visibility', methods=['POST'])
@login_required
def toggle_visibility(trip_id):
    data = request.get_json()
    is_public = data.get('is_public', False)
    
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404
        
    trip.is_public = is_public
    db.session.commit()
    return jsonify({'is_public': trip.is_public}), 200
