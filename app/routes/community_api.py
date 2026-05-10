from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.trip import Trip
from app.models.interaction import Like, Comment
from app.models.user import User

community_api_bp = Blueprint('community_api', __name__, url_prefix='/api/community')

@community_api_bp.route('/feed', methods=['GET'])
def get_feed():
    """Retrieve public trips for the community feed"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    
    trips_query = Trip.query.filter_by(is_public=True).order_by(Trip.created_at.desc())
    pagination = trips_query.paginate(page=page, per_page=per_page)
    
    trips = []
    for trip in pagination.items:
        trips.append({
            'id': trip.id,
            'title': trip.title,
            'destination': trip.destination,
            'image_url': trip.image_url,
            'username': trip.user.username,
            'like_count': trip.likes.count(),
            'comment_count': trip.comments.count(),
            'is_liked': Like.query.filter_by(user_id=current_user.id, trip_id=trip.id).first() is not None if current_user.is_authenticated else False,
            'start_date': trip.start_date.isoformat(),
            'end_date': trip.end_date.isoformat()
        })
        
    return jsonify({
        'trips': trips,
        'has_next': pagination.has_next,
        'next_page': pagination.next_num,
        'total': pagination.total
    }), 200

@community_api_bp.route('/trips/<int:trip_id>/like', methods=['POST'])
@login_required
def toggle_like(trip_id):
    like = Like.query.filter_by(user_id=current_user.id, trip_id=trip_id).first()
    if like:
        db.session.delete(like)
        liked = False
    else:
        new_like = Like(user_id=current_user.id, trip_id=trip_id)
        db.session.add(new_like)
        liked = True
    
    db.session.commit()
    return jsonify({'liked': liked, 'count': Like.query.filter_by(trip_id=trip_id).count()}), 200

@community_api_bp.route('/trips/<int:trip_id>/comments', methods=['GET', 'POST'])
def handle_comments(trip_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({'error': 'Login required'}), 401
            
        data = request.get_json()
        if not data.get('content'):
            return jsonify({'error': 'Content required'}), 400
            
        comment = Comment(user_id=current_user.id, trip_id=trip_id, content=data['content'])
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201
    
    comments = Comment.query.filter_by(trip_id=trip_id).order_by(Comment.created_at.asc()).all()
    return jsonify([c.to_dict() for c in comments]), 200
