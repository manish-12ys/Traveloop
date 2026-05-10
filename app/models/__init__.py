"""
Models module for Traveloop

Phase 1 includes basic User model setup.
Phase 2 includes Trip model for dashboard.
Additional models (Stop, Activity, etc.) will be added in Phase 3.
"""

from app.models.user import User
from app.models.trip import Trip
from app.models.stop import Stop
from app.models.activity import Activity
from app.models.budget import BudgetItem
from app.models.packing import PackingItem
from app.models.note import Note

__all__ = ['User', 'Trip', 'Stop', 'Activity', 'BudgetItem', 'PackingItem', 'Note']


# Phase 1 Models
# - User model (Authentication)

# Phase 2 Models
# - Trip model (Dashboard)

# Phase 3 Models (Implemented)
# - Stop model
# - Activity model
# - Budget model
# - Packing model
# - Notes model
# - SharedLink model (To be implemented in Phase 7)
