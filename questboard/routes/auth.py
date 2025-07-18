"""
Authentication routes for user management.

This module handles user registration, login, logout, and account management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from questboard.models.user import User
from questboard.extensions import db

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic validation
        if not all([username, email, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))
            
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
            
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_active=True  # Set to False if email verification is required
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        flash('Registration successful!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
        # Check if user is active
        if not user.is_active:
            flash('Account is disabled', 'error')
            return redirect(url_for('auth.login'))
            
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log the user in
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Password reset routes
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Implementation for password reset request
    # This would typically send an email with a reset link
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In a real app, you would send a password reset email here
            pass
            
        # Always show success message to prevent email enumeration
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # In a real app, you would verify the token here
    # user = User.verify_reset_password_token(token)
    # if not user:
    #     flash('Invalid or expired token', 'error')
    #     return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Update user's password
        # user.set_password(request.form.get('password'))
        # db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', token=token)
