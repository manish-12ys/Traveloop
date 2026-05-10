"""Authentication routes for signup, login, logout, and current user."""

from urllib.parse import urlparse

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models.user import User


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _is_safe_redirect(target):
    """Allow redirects only within this application."""
    if not target:
        return False

    parsed = urlparse(target)
    return parsed.scheme == '' and parsed.netloc == '' and target.startswith('/')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Render signup form and create new users."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('pages/auth/signup.html')

        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('pages/auth/signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('pages/auth/signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('pages/auth/signup.html')

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('That username is already taken.', 'error')
            return render_template('pages/auth/signup.html')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('That email is already registered.', 'error')
            return render_template('pages/auth/signup.html')

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Welcome to Traveloop. Your account has been created.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('pages/auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Render login form and authenticate users."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not identifier or not password:
            flash('Please enter your username/email and password.', 'error')
            return render_template('pages/auth/login.html')

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user is None or not user.check_password(password):
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('pages/auth/login.html')

        login_user(user, remember=remember)

        next_url = request.args.get('next', '')
        if _is_safe_redirect(next_url):
            return redirect(next_url)

        flash(f'Welcome back, {user.username}.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('pages/auth/login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Render admin login form and authenticate admin users."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('main.admin_dashboard'))

        flash('Your account does not have admin access.', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not identifier or not password:
            flash('Please enter your admin username/email and password.', 'error')
            return render_template('pages/auth/admin_login.html')

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user is None or not user.check_password(password) or not user.is_admin:
            flash('Invalid admin credentials. Please try again.', 'error')
            return render_template('pages/auth/admin_login.html')

        login_user(user, remember=remember)

        next_url = request.args.get('next', '')
        if _is_safe_redirect(next_url):
            return redirect(next_url)

        flash(f'Welcome to the admin dashboard, {user.username}.', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('pages/auth/admin_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """End user session."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/me')
@login_required
def me():
    """Return basic details for the currently authenticated user."""
    return jsonify(
        {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
        }
    )
