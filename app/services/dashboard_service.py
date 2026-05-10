"""Dashboard service - Phase 2"""

from app.models.trip import Trip
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import func


class DashboardService:
    """Service for dashboard-related operations"""
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile information"""
        user = db.session.get(User, user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
        }
    
    @staticmethod
    def get_user_trips(user_id, limit=10, offset=0):
        """Get all trips for a user with pagination."""
        trips = (
            Trip.query.filter_by(user_id=user_id)
            .order_by(Trip.start_date.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [trip.to_dict() for trip in trips]
    
    @staticmethod
    def get_trip(trip_id, user_id):
        """Get a single trip for a user"""
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        return trip.to_dict()
    
    @staticmethod
    def get_trip_count(user_id):
        """Get total trip count for a user."""
        return db.session.query(func.count(Trip.id)).filter_by(user_id=user_id).scalar() or 0
    
    @staticmethod
    def get_active_trips(user_id):
        """Get currently active or upcoming trips"""
        today = datetime.utcnow().date()
        trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.end_date >= today
        ).order_by(Trip.start_date.asc()).all()
        
        return [trip.to_dict() for trip in trips]
    
    @staticmethod
    def get_past_trips(user_id, limit=5):
        """Get past completed trips"""
        today = datetime.utcnow().date()
        trips = Trip.query.filter(
            Trip.user_id == user_id,
            Trip.end_date < today
        ).order_by(Trip.end_date.desc()).limit(limit).all()
        
        return [trip.to_dict() for trip in trips]
    
    @staticmethod
    def get_dashboard_stats(user_id):
        """Get dashboard statistics for a user."""
        all_trips = Trip.query.filter_by(user_id=user_id).all()
        total_trips = len(all_trips)
        total_budget = sum(trip.budget for trip in all_trips) if all_trips else 0

        today = datetime.utcnow().date()
        active_trips = [trip for trip in all_trips if trip.end_date >= today]

        return {
            'total_trips': total_trips,
            'active_trips': len(active_trips),
            'total_budget': total_budget,
            'average_trip_budget': total_budget / total_trips if total_trips > 0 else 0,
        }
    
    @staticmethod
    def create_trip(user_id, title, destination, start_date, end_date, description='', budget=0.0, image_url=''):
        """Create a new trip for a user"""
        trip = Trip(
            user_id=user_id,
            title=title,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            description=description,
            budget=budget,
            image_url=image_url,
            status='planning'
        )
        
        db.session.add(trip)
        db.session.commit()
        
        return trip.to_dict()
    
    @staticmethod
    def update_trip(trip_id, user_id, **kwargs):
        """Update an existing trip"""
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        
        # Only update allowed fields
        allowed_fields = ['title', 'description', 'destination', 'start_date', 'end_date', 'status', 'budget', 'image_url']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(trip, field, value)
        
        db.session.commit()
        return trip.to_dict()
    
    @staticmethod
    def delete_trip(trip_id, user_id):
        """Delete a trip"""
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return False
        
        db.session.delete(trip)
        db.session.commit()
        return True
