"""Core routes and blueprint registration for Traveloop."""

from flask import Blueprint, render_template
from flask_login import login_required

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp

# Create blueprints for different route groups
main_bp = Blueprint('main', __name__)
trips_bp = Blueprint('trips', __name__, url_prefix='/trips')


@main_bp.route('/')
def index():
    """Public home page."""
    return render_template('pages/home.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard page shown after login."""
    return render_template('pages/dashboard.html')


@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'Traveloop API is running'}, 200


from app.routes.trip_api import trip_api_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(trip_api_bp)

@trips_bp.route('/<int:trip_id>')
@login_required
def trip_detail(trip_id):
    """Itinerary Builder page for a specific trip"""
    # Just render the template, javascript will fetch the data
    return render_template('pages/trip_detail.html', trip_id=trip_id)
