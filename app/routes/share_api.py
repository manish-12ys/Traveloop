from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required, current_user
from app.services.share_service import ShareService

share_api_bp = Blueprint('share_api', __name__, url_prefix='/api/share')

@share_api_bp.route('/<int:trip_id>', methods=['GET'])
@login_required
def get_share_link(trip_id):
    from app.models.trip import Trip
    trip = Trip.query.filter_by(id=trip_id, user_id=current_user.id).first()
    if not trip:
        return jsonify({'error': 'Unauthorized or Trip not found'}), 403
        
    link_obj = ShareService.get_or_create_shared_link(trip_id, current_user.id)
    if not link_obj:
        return jsonify({'error': 'Failed to create link'}), 500
    
    link_obj['is_public'] = trip.is_public
    link_obj['full_url'] = request.host_url.rstrip('/') + link_obj['url']
    return jsonify(link_obj), 200

@share_api_bp.route('/<int:trip_id>/toggle', methods=['POST'])
@login_required
def toggle_share(trip_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    
    link = ShareService.toggle_sharing(trip_id, current_user.id, is_active)
    if not link:
        return jsonify({'error': 'Unauthorized or Link not found'}), 403
        
    return jsonify(link), 200

@share_api_bp.route('/clone/<token>', methods=['POST'])
@login_required
def clone_trip(token):
    new_trip_id = ShareService.clone_trip(token, current_user.id)
    if not new_trip_id:
        return jsonify({'error': 'Link expired or invalid'}), 404
        
    return jsonify({
        'message': 'Trip cloned successfully',
        'trip_id': new_trip_id,
        'redirect_url': url_for('trips.trip_detail', trip_id=new_trip_id)
    }), 201
