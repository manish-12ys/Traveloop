from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register user loader callback
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        from app.models.user import User
        return db.session.get(User, int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify, redirect, url_for
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'message': 'Please log in.'}), 401
        return redirect(url_for('auth.login'))
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import render_template
        return render_template('errors/404.html'), 500 # Use 404 for now or create 500.html
    
    # Create tables
    with app.app_context():
        from app.models import User, Trip, Stop, Activity, BudgetItem, PackingItem, Note  # noqa: F401
        from app.models.share import SharedLink  # noqa: F401
        from app.models.interaction import Like, Comment  # noqa: F401
        db.create_all()
    
    return app
