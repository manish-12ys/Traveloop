"""
Models module for Traveloop

Phase 1 includes basic User model setup.
Phase 2 includes Trip model for dashboard.
Additional models (Stop, Activity, etc.) will be added in Phase 3.
"""

from app.models.user import User
from app.models.trip import Trip

__all__ = ['User', 'Trip']


# Phase 1 Models
# - User model (Authentication)

# Phase 2 Models
# - Trip model (Dashboard)

# Phase 3 Models (To be implemented)
# - Stop model
# - Activity model
# - Budget model
# - Packing model
# - Notes model
# - SharedLink model
