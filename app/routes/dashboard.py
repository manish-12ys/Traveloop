"""Dashboard routes - Phase 2"""

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.services.dashboard_service import DashboardService
from datetime import datetime
from app.utils.rate_limiter import limiter, LIMIT_GENEROUS

dashboard_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/profile', methods=['GET'])
@limiter.limit(LIMIT_GENEROUS)
@login_required
def get_profile():
    """Get current user profile"""
    profile = DashboardService.get_user_profile(current_user.id)
    if not profile:
        return {'error': 'User not found'}, 404
    return jsonify(profile), 200


@dashboard_bp.route('/trips', methods=['GET'])
@limiter.limit(LIMIT_GENEROUS)
@login_required
def get_trips():
    """Get user's trips with pagination"""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    trips = DashboardService.get_user_trips(current_user.id, limit, offset)
    total_count = DashboardService.get_trip_count(current_user.id)
    
    return jsonify({
        'trips': trips,
        'total': total_count,
        'limit': limit,
        'offset': offset,
    }), 200


@dashboard_bp.route('/active-trips', methods=['GET'])
@limiter.limit(LIMIT_GENEROUS)
@login_required
def get_active_trips():
    """Get user's active/upcoming trips"""
    trips = DashboardService.get_active_trips(current_user.id)
    return jsonify({'trips': trips}), 200


@dashboard_bp.route('/past-trips', methods=['GET'])
@login_required
def get_past_trips():
    """Get user's past trips"""
    limit = request.args.get('limit', 5, type=int)
    trips = DashboardService.get_past_trips(current_user.id, limit)
    return jsonify({'trips': trips}), 200


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get dashboard statistics"""
    stats = DashboardService.get_dashboard_stats(current_user.id)
    return jsonify(stats), 200


@dashboard_bp.route('/trips', methods=['POST'])
@login_required
def create_trip():
    """Create a new trip"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'destination', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return {'error': 'Missing required fields'}, 400
    
    try:
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date']).date()
        end_date = datetime.fromisoformat(data['end_date']).date()
        
        if start_date > end_date:
            return {'error': 'Start date must be before end date'}, 400
        
        trip = DashboardService.create_trip(
            user_id=current_user.id,
            title=data['title'],
            destination=data['destination'],
            start_date=start_date,
            end_date=end_date,
            description=data.get('description', ''),
            budget=data.get('budget', 0.0),
            image_url=data.get('image_url', '')
        )
        
        return jsonify(trip), 201
    
    except (ValueError, KeyError) as e:
        return {'error': f'Invalid data: {str(e)}'}, 400


@dashboard_bp.route('/trips/<int:trip_id>', methods=['GET', 'PUT'])
@login_required
def manage_trip(trip_id):
    """Get or update a single trip"""
    if request.method == 'GET':
        trip = DashboardService.get_trip(trip_id, current_user.id)
        if not trip:
            return {'error': 'Trip not found'}, 404
        return jsonify(trip), 200

    # PUT
    data = request.get_json()
    try:
        if 'start_date' in data:
            data['start_date'] = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data:
            data['end_date'] = datetime.fromisoformat(data['end_date']).date()

        trip = DashboardService.update_trip(trip_id, current_user.id, **data)
        if not trip:
            return {'error': 'Trip not found'}, 404
        return jsonify(trip), 200

    except (ValueError, KeyError) as e:
        return {'error': f'Invalid data: {str(e)}'}, 400



@dashboard_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    """Delete a trip"""
    success = DashboardService.delete_trip(trip_id, current_user.id)
    
    if not success:
        return {'error': 'Trip not found'}, 404
    
    return {'message': 'Trip deleted successfully'}, 200
