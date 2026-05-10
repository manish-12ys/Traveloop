"""Trip Service for Phase 3 models"""

from app import db
from app.models.stop import Stop
from app.models.activity import Activity
from app.models.budget import BudgetItem
from app.models.packing import PackingItem
from app.models.note import Note
from app.models.trip import Trip

class TripService:
    """Service for trip specific operations (stops, activities, budget, etc.)"""

    # --- Stops ---
    @staticmethod
    def get_trip_stops(trip_id):
        return [stop.to_dict() for stop in Stop.query.filter_by(trip_id=trip_id).order_by(Stop.order).all()]

    @staticmethod
    def add_stop(trip_id, name, location, arrival_date, departure_date):
        # Get max order
        max_order_stop = Stop.query.filter_by(trip_id=trip_id).order_by(Stop.order.desc()).first()
        new_order = max_order_stop.order + 1 if max_order_stop else 0
        
        stop = Stop(
            trip_id=trip_id,
            name=name,
            location=location,
            arrival_date=arrival_date,
            departure_date=departure_date,
            order=new_order
        )
        db.session.add(stop)
        db.session.commit()
        return stop.to_dict()

    @staticmethod
    def update_stop(stop_id, trip_id, **kwargs):
        stop = Stop.query.filter_by(id=stop_id, trip_id=trip_id).first()
        if not stop:
            return None
        
        allowed_fields = ['name', 'location', 'arrival_date', 'departure_date']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(stop, field, value)
        
        db.session.commit()
        return stop.to_dict()

    @staticmethod
    def delete_stop(stop_id, trip_id):
        stop = Stop.query.filter_by(id=stop_id, trip_id=trip_id).first()
        if not stop:
            return False
        db.session.delete(stop)
        db.session.commit()
        return True

    # --- Activities ---
    @staticmethod
    def get_trip_activities(trip_id):
        return [activity.to_dict() for activity in Activity.query.filter_by(trip_id=trip_id).order_by(Activity.order).all()]

    @staticmethod
    def add_activity(trip_id, title, stop_id=None, description='', start_time=None, end_time=None, cost=0.0):
        max_order_activity = Activity.query.filter_by(trip_id=trip_id).order_by(Activity.order.desc()).first()
        new_order = max_order_activity.order + 1 if max_order_activity else 0

        activity = Activity(
            trip_id=trip_id,
            stop_id=stop_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            cost=cost,
            order=new_order
        )
        db.session.add(activity)
        db.session.commit()
        return activity.to_dict()

    @staticmethod
    def update_activity(activity_id, trip_id, **kwargs):
        activity = Activity.query.filter_by(id=activity_id, trip_id=trip_id).first()
        if not activity:
            return None
        
        allowed_fields = ['title', 'description', 'start_time', 'end_time', 'cost', 'stop_id']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(activity, field, value)
                
        db.session.commit()
        return activity.to_dict()

    @staticmethod
    def delete_activity(activity_id, trip_id):
        activity = Activity.query.filter_by(id=activity_id, trip_id=trip_id).first()
        if not activity:
            return False
        db.session.delete(activity)
        db.session.commit()
        return True

    @staticmethod
    def reorder_activities(trip_id, activity_ids):
        """Update the order of activities based on the provided list of IDs"""
        activities = Activity.query.filter_by(trip_id=trip_id).all()
        activity_map = {a.id: a for a in activities}
        
        for index, act_id in enumerate(activity_ids):
            if act_id in activity_map:
                activity_map[act_id].order = index
                
        db.session.commit()
        return True

    # --- Budget Items ---
    @staticmethod
    def get_trip_budget_items(trip_id):
        return [item.to_dict() for item in BudgetItem.query.filter_by(trip_id=trip_id).all()]

    @staticmethod
    def add_budget_item(trip_id, category, description='', expected_amount=0.0, actual_amount=0.0):
        item = BudgetItem(
            trip_id=trip_id,
            category=category,
            description=description,
            expected_amount=expected_amount,
            actual_amount=actual_amount
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    @staticmethod
    def update_budget_item(item_id, trip_id, **kwargs):
        item = BudgetItem.query.filter_by(id=item_id, trip_id=trip_id).first()
        if not item:
            return None
        
        allowed_fields = ['category', 'description', 'expected_amount', 'actual_amount']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(item, field, value)
                
        db.session.commit()
        return item.to_dict()

    @staticmethod
    def delete_budget_item(item_id, trip_id):
        item = BudgetItem.query.filter_by(id=item_id, trip_id=trip_id).first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    # --- Packing Items ---
    @staticmethod
    def get_trip_packing_items(trip_id):
        return [item.to_dict() for item in PackingItem.query.filter_by(trip_id=trip_id).all()]

    @staticmethod
    def add_packing_item(trip_id, item_name, category='General'):
        item = PackingItem(
            trip_id=trip_id,
            item_name=item_name,
            category=category
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    @staticmethod
    def toggle_packing_item(item_id, trip_id, is_packed):
        item = PackingItem.query.filter_by(id=item_id, trip_id=trip_id).first()
        if not item:
            return None
        item.is_packed = is_packed
        db.session.commit()
        return item.to_dict()

    @staticmethod
    def delete_packing_item(item_id, trip_id):
        item = PackingItem.query.filter_by(id=item_id, trip_id=trip_id).first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    # --- Notes ---
    @staticmethod
    def get_trip_notes(trip_id):
        return [note.to_dict() for note in Note.query.filter_by(trip_id=trip_id).all()]

    @staticmethod
    def add_note(trip_id, content, title=''):
        note = Note(
            trip_id=trip_id,
            content=content,
            title=title
        )
        db.session.add(note)
        db.session.commit()
        return note.to_dict()

    @staticmethod
    def update_note(note_id, trip_id, content, title=None):
        note = Note.query.filter_by(id=note_id, trip_id=trip_id).first()
        if not note:
            return None
        note.content = content
        if title is not None:
            note.title = title
        db.session.commit()
        return note.to_dict()

    @staticmethod
    def delete_note(note_id, trip_id):
        note = Note.query.filter_by(id=note_id, trip_id=trip_id).first()
        if not note:
            return False
        db.session.delete(note)
        db.session.commit()
        return True
