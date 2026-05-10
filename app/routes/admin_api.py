"""
Admin Analytics API — Phase 8
Provides site-wide statistics for the admin dashboard.
All endpoints are protected by @admin_required.
"""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.trip import Trip
from app.models.stop import Stop
from app.models.activity import Activity
from app.models.interaction import Like, Comment
from app.models.share import SharedLink
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')


def admin_required(f):
    """Decorator that restricts access to admin users only."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


@admin_api_bp.route('/stats/overview', methods=['GET'])
@admin_required
def overview_stats():
    """High-level platform statistics."""
    total_users = User.query.count()
    total_trips = Trip.query.count()
    total_stops = Stop.query.count()
    total_activities = Activity.query.count()
    total_likes = Like.query.count()
    total_comments = Comment.query.count()
    public_trips = Trip.query.filter_by(is_public=True).count()

    # New users last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
    new_trips_30d = Trip.query.filter(Trip.created_at >= thirty_days_ago).count()

    return jsonify({
        'total_users': total_users,
        'total_trips': total_trips,
        'total_stops': total_stops,
        'total_activities': total_activities,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'public_trips': public_trips,
        'new_users_30d': new_users_30d,
        'new_trips_30d': new_trips_30d,
    }), 200


@admin_api_bp.route('/stats/top-destinations', methods=['GET'])
@admin_required
def top_destinations():
    """Top destinations by trip count."""
    results = db.session.query(
        Trip.destination,
        func.count(Trip.id).label('count')
    ).group_by(Trip.destination)\
     .order_by(desc('count'))\
     .limit(10).all()

    return jsonify([
        {'destination': r.destination, 'count': r.count}
        for r in results
    ]), 200


@admin_api_bp.route('/stats/user-activity', methods=['GET'])
@admin_required
def user_activity():
    """User and trip registration over the last 30 days (daily)."""
    days = []
    for i in range(29, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        user_count = User.query.filter(
            User.created_at >= day_start,
            User.created_at <= day_end
        ).count()

        trip_count = Trip.query.filter(
            Trip.created_at >= day_start,
            Trip.created_at <= day_end
        ).count()

        days.append({
            'date': day.isoformat(),
            'users': user_count,
            'trips': trip_count,
        })

    return jsonify(days), 200


@admin_api_bp.route('/stats/top-users', methods=['GET'])
@admin_required
def top_users():
    """Most active users by trip count."""
    results = db.session.query(
        User.id,
        User.username,
        User.email,
        User.is_admin,
        User.created_at,
        func.count(Trip.id).label('trip_count')
    ).outerjoin(Trip, Trip.user_id == User.id)\
     .group_by(User.id)\
     .order_by(desc('trip_count'))\
     .limit(10).all()

    return jsonify([{
        'id': r.id,
        'username': r.username,
        'email': r.email,
        'is_admin': r.is_admin,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'trip_count': r.trip_count
    } for r in results]), 200


@admin_api_bp.route('/stats/popular-activities', methods=['GET'])
@admin_required
def popular_activities():
    """Most frequently used activity titles."""
    results = db.session.query(
        Activity.title,
        func.count(Activity.id).label('count')
    ).group_by(Activity.title)\
     .order_by(desc('count'))\
     .limit(10).all()

    return jsonify([
        {'title': r.title, 'count': r.count}
        for r in results
    ]), 200


@admin_api_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """Paginated list of all users."""
    users = db.session.query(
        User.id, User.username, User.email, User.is_admin, User.created_at,
        func.count(Trip.id).label('trip_count')
    ).outerjoin(Trip, Trip.user_id == User.id)\
     .group_by(User.id)\
     .order_by(User.created_at.desc()).all()

    return jsonify([{
        'id': r.id,
        'username': r.username,
        'email': r.email,
        'is_admin': r.is_admin,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'trip_count': r.trip_count
    } for r in users]), 200


@admin_api_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Grant or revoke admin access for a user."""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username, 'is_admin': user.is_admin}), 200
