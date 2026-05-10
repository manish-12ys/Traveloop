"""Budget Item model - Phase 3"""

from app import db
from datetime import datetime

class BudgetItem(db.Model):
    """BudgetItem model for tracking expenses during a trip"""
    __tablename__ = 'budget_items'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)  # Transport, Accommodation, Food, etc.
    description = db.Column(db.String(255), default='')
    expected_amount = db.Column(db.Float, default=0.0)
    actual_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert budget item to dictionary for JSON responses"""
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'category': self.category,
            'description': self.description,
            'expected_amount': self.expected_amount,
            'actual_amount': self.actual_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<BudgetItem {self.category}>'
