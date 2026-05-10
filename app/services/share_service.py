from app import db
from app.models.share import SharedLink
from app.models.trip import Trip
from app.models.stop import Stop
from app.models.activity import Activity
import uuid
import logging

logger = logging.getLogger(__name__)

class ShareService:
    @staticmethod
    def get_or_create_shared_link(trip_id, user_id):
        """Generate or retrieve an active sharing token for a trip"""
        # Verify ownership
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
            
        link = SharedLink.query.filter_by(trip_id=trip_id).first()
        if not link:
            link = SharedLink(trip_id=trip_id)
            db.session.add(link)
            db.session.commit()
        
        return link.to_dict()

    @staticmethod
    def toggle_sharing(trip_id, user_id, is_active):
        """Enable or disable sharing for a trip"""
        link = SharedLink.query.join(Trip).filter(
            SharedLink.trip_id == trip_id,
            Trip.user_id == user_id
        ).first()
        
        if not link:
            return None
            
        link.is_active = is_active
        db.session.commit()
        return link.to_dict()

    @staticmethod
    def get_trip_by_token(token):
        """Retrieve a trip by its sharing token if active"""
        link = SharedLink.query.filter_by(token=token, is_active=True).first()
        if not link:
            return None
            
        # Increment view count
        link.view_count += 1
        db.session.commit()
        
        return link.trip

    @staticmethod
    def clone_trip(token, target_user_id):
        """Clone a shared trip into a user's own account"""
        source_trip = ShareService.get_trip_by_token(token)
        if not source_trip:
            return None
            
        # 1. Clone Trip object
        new_trip = Trip(
            user_id=target_user_id,
            title=f"Copy of {source_trip.title}",
            destination=source_trip.destination,
            description=source_trip.description,
            start_date=source_trip.start_date,
            end_date=source_trip.end_date,
            budget=source_trip.budget,
            image_url=source_trip.image_url
        )
        db.session.add(new_trip)
        db.session.flush() # Get new_trip.id
        
        # 2. Clone Stops
        stop_map = {} # old_id -> new_id for activity mapping
        for stop in source_trip.stops:
            new_stop = Stop(
                trip_id=new_trip.id,
                name=stop.name,
                location=stop.location,
                arrival_date=stop.arrival_date,
                departure_date=stop.departure_date,
                latitude=stop.latitude,
                longitude=stop.longitude,
                order=stop.order
            )
            db.session.add(new_stop)
            db.session.flush()
            stop_map[stop.id] = new_stop.id
            
        # 3. Clone Activities
        for act in source_trip.activities:
            new_act = Activity(
                trip_id=new_trip.id,
                stop_id=stop_map.get(act.stop_id),
                title=act.title,
                description=act.description,
                start_time=act.start_time,
                end_time=act.end_time,
                cost=act.cost,
                order=act.order
            )
            db.session.add(new_act)
            
        db.session.commit()
        return new_trip.id
