"""Rate limiting configuration for Traveloop API."""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize limiter (will be configured in app factory)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use in-memory storage for development
)

# Common rate limit patterns
LIMIT_STRICT = "5 per minute"      # For auth/sensitive endpoints
LIMIT_NORMAL = "30 per minute"     # For standard API endpoints  
LIMIT_GENEROUS = "100 per minute"  # For read-only endpoints
