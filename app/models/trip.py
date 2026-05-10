"""Trip model - Phase 2 Dashboard"""

from app import db
from datetime import datetime


class Trip(db.Model):
    """Trip model for user travel plans"""
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    destination = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='planning', nullable=False)  # planning, ongoing, completed
    budget = db.Column(db.Float, default=0.0)
    image_url = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('trips', lazy='dynamic', cascade='all, delete-orphan'))
    stops = db.relationship('Stop', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    budget_items = db.relationship('BudgetItem', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    packing_items = db.relationship('PackingItem', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert trip to dictionary for JSON responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'budget': self.budget,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Trip {self.title}>'
