from app import db
from datetime import datetime
import uuid

class SharedLink(db.Model):
    __tablename__ = 'shared_links'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    trip = db.relationship('Trip', backref=db.backref('shared_links', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'token': self.token,
            'is_active': self.is_active,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat(),
            'url': f"/share/{self.token}"
        }
