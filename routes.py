import os
import uuid
import logging
from datetime import datetime
import jinja2
from flask import (
    render_template, request, redirect, url_for, flash, 
    current_app, get_flashed_messages, session
)
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Character, CharacterTemplate, Scenario, Achievement, ScenarioCompletion, ScavengerHuntTask, TaskSubmission
from utils import generate_character, generate_character_from_template
from photo_verification import save_photo, verify_photo_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_template_exists(template_path):
    """Verify if a template file exists with improved error handling"""
    try:
        template_loader = current_app.jinja_env.loader
        if not template_loader:
            logger.error("Template loader not initialized")
            return False
            
        template = template_loader.get_source(current_app.jinja_env, template_path)[0]
        logger.debug(f"Template verified successfully: {template_path}")
        return True
    except Exception as e:
        logger.error(f"Error verifying template {template_path}: {str(e)}")
        return False

def render_template_safe(template_name, **context):
    """Safe template rendering with enhanced error handling and logging"""
    try:
        # Add common context variables
        base_context = {
            'get_flashed_messages': get_flashed_messages,
            'url_for': url_for,
            'current_user': current_user,
            'config': current_app.config,
            'error_id': str(uuid.uuid4()),
            'error_path': request.path,
            'error_referrer': request.referrer,
            'timestamp': datetime.utcnow()
        }
        base_context.update(context)

        if not verify_template_exists(template_name):
            logger.error(f"Template not found: {template_name}")
            return render_template('500.html', error_message="Template not found", **base_context)

        return render_template(template_name, **base_context)
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"Template rendering error: {str(e)} (Error ID: {error_id})")
        return render_template('500.html', error_id=error_id, error_message=str(e), **base_context)

def register_routes(app):
    """Register all application routes with improved error handling"""
    try:
        logger.info("Starting route registration")
        
        # Push application context
        with app.app_context():
            # Define routes with their handlers
            routes = [
                ('/', 'index', index, ['GET']),
                ('/register', 'register', register, ['GET', 'POST']),
                ('/login', 'login', login, ['GET', 'POST']),
                ('/logout', 'logout', logout, ['GET']),
                ('/profile', 'profile', profile, ['GET']),
                ('/update_profile', 'update_profile', update_profile, ['POST']),
                ('/create_character', 'create_new_character', create_new_character, ['GET', 'POST']),
                ('/character/<int:char_id>', 'view_character', view_character, ['GET']),
                ('/create_template', 'create_template', create_template, ['GET', 'POST']),
                ('/view_scenario', 'view_scenario', view_scenario, ['GET']),
                ('/scavenger_hunt/<int:scenario_id>', 'scavenger_hunt', scavenger_hunt, ['GET']),
                ('/submit_task/<int:task_id>', 'submit_task', submit_task, ['POST'])
            ]
            
            # Register routes with error handling
            for path, endpoint, handler, methods in routes:
                try:
                    app.add_url_rule(path, endpoint, handler, methods=methods)
                    logger.info(f"Registered route: {endpoint} ({path})")
                except Exception as e:
                    logger.error(f"Failed to register route {endpoint}: {str(e)}")
                    raise RuntimeError(f"Route registration failed for {endpoint}: {str(e)}")
            
            # Register error handlers
            app.errorhandler(404)(lambda e: render_template_safe('404.html'))
            app.errorhandler(500)(lambda e: render_template_safe('500.html'))
            
            logger.info("Route registration completed successfully")
            return app
            
    except Exception as e:
        logger.error(f"Route registration failed: {str(e)}")
        raise RuntimeError(f"Failed to register routes: {str(e)}")

def index():
    """Handle index route"""
    templates = []
    if current_user.is_authenticated:
        templates = CharacterTemplate.query.filter_by(user_id=current_user.id).all()
    return render_template_safe('index.html', templates=templates)

def register():
    """Handle user registration"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
                
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('register'))
                
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
                
    return render_template_safe('auth/register.html')

def login():
    """Handle user login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = bool(request.form.get('remember'))
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            flash('Invalid email or password', 'error')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Login failed. Please try again.', 'error')
            
    return render_template_safe('auth/login.html')

@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@login_required
def profile():
    """Handle user profile view"""
    return render_template_safe('auth/profile.html')

@login_required
def update_profile():
    """Handle profile updates"""
    try:
        current_user.gender = request.form.get('gender')
        current_user.spiciness_level = int(request.form.get('spiciness_level', 1))
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        flash('Failed to update profile.', 'error')
    return redirect(url_for('profile'))

@login_required
def create_new_character():
    """Handle character creation"""
    try:
        template_id = request.form.get('template_id')
        if template_id:
            template = CharacterTemplate.query.get(template_id)
            character_data = generate_character_from_template(template)
        else:
            character_data = generate_character()
        
        character = Character(**character_data)
        if current_user.is_authenticated:
            character.user_id = current_user.id
        
        db.session.add(character)
        db.session.commit()
        
        return redirect(url_for('view_character', char_id=character.id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Character creation error: {str(e)}")
        flash('Failed to create character.', 'error')
        return redirect(url_for('index'))

def view_character(char_id):
    """Handle character view"""
    try:
        character = Character.query.get_or_404(char_id)
        return render_template_safe('character.html', character=character)
    except Exception as e:
        logger.error(f"Error viewing character: {str(e)}")
        flash('Character not found.', 'error')
        return redirect(url_for('index'))

@login_required
def create_template():
    """Handle template creation"""
    if request.method == 'POST':
        try:
            template = CharacterTemplate(
                name=request.form.get('name'),
                description=request.form.get('description'),
                user_id=current_user.id,
                height_options=request.form.get('height_options'),
                hair_color_options=request.form.get('hair_color_options'),
                eye_color_options=request.form.get('eye_color_options'),
                style_preference_options=request.form.get('style_preference_options'),
                occupation_options=request.form.get('occupation_options'),
                hobbies_options=request.form.get('hobbies_options'),
                quirks_options=request.form.get('quirks_options')
            )
            db.session.add(template)
            db.session.commit()
            flash('Template created successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Template creation error: {str(e)}")
            flash('Failed to create template.', 'error')
    return render_template_safe('create_template.html')

@login_required
def view_scenario():
    """Handle scenario view"""
    try:
        scenarios = Scenario.query.all()
        completions = ScenarioCompletion.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        return render_template_safe('scenario.html', 
                                scenarios=scenarios, 
                                completions=completions,
                                achievements=achievements)
    except Exception as e:
        logger.error(f"Error viewing scenarios: {str(e)}")
        flash('Failed to load scenarios.', 'error')
        return redirect(url_for('index'))

@login_required
def scavenger_hunt(scenario_id):
    """Handle scavenger hunt"""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        tasks = ScavengerHuntTask.query.filter_by(scenario_id=scenario_id).all()
        return render_template_safe('scavenger_hunt.html', 
                                scenario=scenario,
                                tasks=tasks)
    except Exception as e:
        logger.error(f"Error loading scavenger hunt: {str(e)}")
        flash('Failed to load scavenger hunt.', 'error')
        return redirect(url_for('view_scenario'))

@login_required
def submit_task(task_id):
    """Handle task submission"""
    try:
        task = ScavengerHuntTask.query.get_or_404(task_id)
        if 'photo' not in request.files:
            flash('No photo uploaded', 'error')
            return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))

        photo = request.files['photo']
        if not photo.filename:
            flash('No photo selected', 'error')
            return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))

        photo_path = save_photo(photo)
        is_verified, confidence = verify_photo_content(
            photo_path,
            task.required_objects,
            task.object_confidence,
            task.required_pose,
            task.required_location
        )

        submission = TaskSubmission(
            task_id=task.id,
            user_id=current_user.id,
            photo_path=photo_path,
            confidence_score=confidence,
            is_verified=is_verified
        )
        db.session.add(submission)
        db.session.commit()

        if is_verified:
            flash('Task completed successfully!', 'success')
        else:
            flash('Photo verification failed. Please try again.', 'warning')

        return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Task submission error: {str(e)}")
        flash('Failed to submit task.', 'error')
        return redirect(url_for('view_scenario'))
