"""Note model - Phase 3"""

from app import db
from datetime import datetime

class Note(db.Model):
    """Note model for general trip notes"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    title = db.Column(db.String(255), default='')
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert note to dictionary for JSON responses"""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Note {self.id}>'
