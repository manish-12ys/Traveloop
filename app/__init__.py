from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
import click
import os
from datetime import date, datetime
from sqlalchemy import inspect, text
from app.utils.rate_limiter import limiter

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

    @app.template_filter('indian_date')
    def indian_date(value):
        if not value:
            return ''

        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value

        if isinstance(value, datetime):
            value = value.date()

        if isinstance(value, date):
            return value.strftime('%d/%m/%Y')

        return str(value)

    @app.template_filter('indian_currency')
    def indian_currency(value):
        try:
            amount = float(value or 0)
        except (TypeError, ValueError):
            amount = 0.0

        return f"₹{amount:,.2f}"
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
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

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def create_admin(username, email, password):
        """Create a new admin user or promote an existing user."""
        from app.models.user import User

        normalized_email = email.strip().lower()
        user = User.query.filter(
            (User.username == username) | (User.email == normalized_email)
        ).first()

        if user is None:
            user = User(username=username.strip(), email=normalized_email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            action = 'Created'
        else:
            user.is_admin = True
            if password:
                user.set_password(password)
            action = 'Promoted'

        db.session.commit()
        click.echo(f'{action} admin user: {user.username} <{user.email}>')
    
    # Create tables
    with app.app_context():
        from app.models import User, Trip, Stop, Activity, BudgetItem, PackingItem, Note  # noqa: F401
        from app.models.share import SharedLink  # noqa: F401
        from app.models.interaction import Like, Comment  # noqa: F401
        db.create_all()

        inspector = inspect(db.engine)
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "is_admin" not in user_columns:
            db.session.execute(
                text(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"
                )
            )
            db.session.commit()
    
    return app
