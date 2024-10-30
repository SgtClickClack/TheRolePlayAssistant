from flask import render_template, request, session, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion, User, ScavengerHuntTask, TaskSubmission
from utils import generate_character as create_character_data, get_random_scenario, generate_character_from_template
from photo_verification import verify_photo_content, save_photo, allowed_file
import uuid
from datetime import datetime, timedelta
import logging
import traceback

logger = logging.getLogger(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Get form data and validate
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            remember = request.form.get('remember', False)
            
            # Validate required fields
            if not email:
                flash('Email is required', 'error')
                return render_template('auth/login.html')
            if not password:
                flash('Password is required', 'error')
                return render_template('auth/login.html')
            
            # Find user and verify credentials
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                # Clear any existing session
                session.clear()
                
                # Set up new session
                session['session_id'] = str(uuid.uuid4())
                session.permanent = True
                session.permanent_session_lifetime = timedelta(days=7 if remember else 1)
                
                # Log in user
                login_user(user, remember=bool(remember))
                logger.info(f"User {email} logged in successfully")
                
                # Handle next page redirect
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                
                return redirect(next_page)
            
            # Invalid credentials
            logger.warning(f"Failed login attempt for email: {email}")
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
            db.session.rollback()
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('auth/login.html')
    
    # GET request - render login form
    return render_template('auth/login.html')
