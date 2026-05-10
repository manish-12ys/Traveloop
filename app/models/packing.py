"""Packing Item model - Phase 3"""

from app import db
from datetime import datetime

class PackingItem(db.Model):
    """PackingItem model for trip checklist"""
    __tablename__ = 'packing_items'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    item_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default='General')
    is_packed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert packing item to dictionary for JSON responses"""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'item_name': self.item_name,
            'category': self.category,
            'is_packed': self.is_packed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<PackingItem {self.item_name}>'
