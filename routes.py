import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from flask import (
    render_template, request, redirect, url_for, flash, 
    current_app, get_flashed_messages, session, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models import (
    db, User, Character, CharacterTemplate, Scenario, Achievement, 
    ScenarioCompletion, ScavengerHuntTask, TaskSubmission
)
from utils import generate_character, generate_character_from_template
from story_generator import generate_story_scene
from photo_verification import save_photo, verify_photo_content, cleanup_old_photos

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_database_error(e: SQLAlchemyError, operation: str) -> None:
    """Handle database errors consistently"""
    error_id = str(uuid.uuid4())
    logger.error(f"Database error during {operation} (Error ID: {error_id}): {str(e)}")
    db.session.rollback()
    flash(f"An error occurred. Reference ID: {error_id}", 'error')

def verify_template_exists(template_path: str) -> bool:
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

def render_template_safe(template_name: str, **context) -> str:
    """Safe template rendering with enhanced error handling and logging"""
    try:
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
            ('/generate_story/<int:char_id>/<int:scenario_id>', 'generate_story', generate_story, ['GET']),
            ('/view_story/<int:char_id>/<int:scenario_id>', 'view_story', view_story, ['GET']),
            ('/scavenger_hunt/<int:scenario_id>', 'scavenger_hunt', scavenger_hunt, ['GET']),
            ('/submit_task/<int:task_id>', 'submit_task', submit_task, ['POST'])
        ]
        
        for path, endpoint, handler, methods in routes:
            try:
                app.add_url_rule(path, endpoint, handler, methods=methods)
                logger.info(f"Registered route: {endpoint} ({path})")
            except Exception as e:
                logger.error(f"Failed to register route {endpoint}: {str(e)}")
                raise RuntimeError(f"Route registration failed for {endpoint}")
        
        @app.errorhandler(404)
        def not_found_error(e):
            return render_template_safe('404.html'), 404

        @app.errorhandler(500)
        def internal_error(e):
            db.session.rollback()
            return render_template_safe('500.html', error=str(e)), 500

        @app.errorhandler(HTTPException)
        def handle_http_error(e):
            return render_template_safe('500.html', error=str(e)), e.code
        
        logger.info("Route registration completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Route registration failed: {str(e)}")
        raise RuntimeError(f"Failed to register routes: {str(e)}")

def index():
    """Handle index route with error handling"""
    try:
        templates = []
        if current_user.is_authenticated:
            templates = CharacterTemplate.query.filter_by(user_id=current_user.id).all()
        return render_template_safe('index.html', templates=templates)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template_safe('500.html', error="Failed to load index page")

def register():
    """Handle user registration with improved validation and error handling"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not all([username, email, password]):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))
            
            if len(username) < 3 or len(username) > 80:
                flash('Username must be between 3 and 80 characters', 'error')
                return redirect(url_for('register'))
            
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
            
        except SQLAlchemyError as e:
            handle_database_error(e, "user registration")
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
                
    return render_template_safe('auth/register.html')

def login():
    """Handle user login with improved security and error handling"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            if not email or not password:
                flash('Email and password are required', 'error')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                
                session.clear()
                session['_fresh'] = True
                
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                return redirect(next_page)
                
            flash('Invalid email or password', 'error')
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Login failed. Please try again.', 'error')
            
    return render_template_safe('auth/login.html')

@login_required
def logout():
    """Handle user logout with session cleanup"""
    try:
        session.clear()
        logout_user()
        flash('You have been logged out.', 'info')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        flash('Logout failed. Please try again.', 'error')
    return redirect(url_for('index'))

@login_required
def profile():
    """Handle user profile view with error handling"""
    try:
        return render_template_safe('auth/profile.html')
    except Exception as e:
        logger.error(f"Profile view error: {str(e)}")
        flash('Failed to load profile.', 'error')
        return redirect(url_for('index'))

@login_required
def update_profile():
    """Handle profile updates with validation"""
    try:
        gender = request.form.get('gender')
        spiciness_level = request.form.get('spiciness_level')
        
        if gender not in ['male', 'female', 'other']:
            flash('Invalid gender selection', 'error')
            return redirect(url_for('profile'))
            
        if spiciness_level not in ['1', '2', '3']:
            flash('Invalid spiciness level', 'error')
            return redirect(url_for('profile'))
            
        current_user.gender = gender
        current_user.spiciness_level = int(spiciness_level)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except SQLAlchemyError as e:
        handle_database_error(e, "profile update")
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        flash('Failed to update profile.', 'error')
        
    return redirect(url_for('profile'))

@login_required
def create_new_character():
    """Handle character creation with improved error handling"""
    try:
        template_id = request.form.get('template_id')
        if template_id:
            template = CharacterTemplate.query.get_or_404(template_id)
            if template.user_id != current_user.id:
                abort(403)
            character_data = generate_character_from_template(template)
        else:
            character_data = generate_character()
        
        character = Character(**character_data)
        character.user_id = current_user.id
        
        db.session.add(character)
        db.session.commit()
        
        return redirect(url_for('view_character', char_id=character.id))
        
    except SQLAlchemyError as e:
        handle_database_error(e, "character creation")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Character creation error: {str(e)}")
        flash('Failed to create character.', 'error')
        return redirect(url_for('index'))

@login_required
def view_character(char_id):
    """Handle character view with access control"""
    try:
        character = Character.query.get_or_404(char_id)
        if character.user_id != current_user.id:
            abort(403)
        return render_template_safe('character.html', character=character)
    except Exception as e:
        logger.error(f"Error viewing character: {str(e)}")
        flash('Character not found.', 'error')
        return redirect(url_for('index'))

@login_required
def create_template():
    """Handle template creation with validation"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name or not description:
                flash('Name and description are required', 'error')
                return redirect(url_for('create_template'))
                
            template = CharacterTemplate(
                name=name,
                description=description,
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
            
        except SQLAlchemyError as e:
            handle_database_error(e, "template creation")
        except Exception as e:
            logger.error(f"Template creation error: {str(e)}")
            flash('Failed to create template.', 'error')
            
    return render_template_safe('create_template.html')

@login_required
def view_scenario():
    """Handle scenario view with error handling"""
    try:
        scenarios = Scenario.query.all()
        completions = ScenarioCompletion.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        
        return render_template_safe('scenario.html', 
                                scenarios=scenarios, 
                                completions=completions,
                                achievements=achievements)
    except SQLAlchemyError as e:
        handle_database_error(e, "scenario view")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error viewing scenarios: {str(e)}")
        flash('Failed to load scenarios.', 'error')
        return redirect(url_for('index'))

@login_required
def generate_story(char_id, scenario_id):
    """Handle story generation with access control"""
    try:
        character = Character.query.get_or_404(char_id)
        scenario = Scenario.query.get_or_404(scenario_id)
        
        if character.user_id != current_user.id:
            abort(403)
        
        story_scene = generate_story_scene(character, scenario)
        session['current_story'] = story_scene
        
        return redirect(url_for('view_story', char_id=char_id, scenario_id=scenario_id))
    except Exception as e:
        logger.error(f"Story generation error: {str(e)}")
        flash('Failed to generate story.', 'error')
        return redirect(url_for('view_scenario'))

@login_required
def view_story(char_id, scenario_id):
    """Handle story view with session management"""
    try:
        character = Character.query.get_or_404(char_id)
        scenario = Scenario.query.get_or_404(scenario_id)
        
        if character.user_id != current_user.id:
            abort(403)
        
        story_scene = session.get('current_story')
        if not story_scene:
            story_scene = generate_story_scene(character, scenario)
            session['current_story'] = story_scene
            
        return render_template_safe('story.html',
                                character=character,
                                scenario=scenario,
                                story=story_scene)
    except Exception as e:
        logger.error(f"Error viewing story: {str(e)}")
        flash('Failed to load story.', 'error')
        return redirect(url_for('view_scenario'))

@login_required
def scavenger_hunt(scenario_id):
    """Handle scavenger hunt view with error handling"""
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        tasks = ScavengerHuntTask.query.filter_by(scenario_id=scenario_id).all()
        
        for task in tasks:
            task.submissions = TaskSubmission.query.filter_by(
                task_id=task.id,
                user_id=current_user.id
            ).order_by(TaskSubmission.submitted_at.desc()).all()
        
        return render_template_safe('scavenger_hunt.html',
                                scenario=scenario,
                                tasks=tasks)
    except Exception as e:
        logger.error(f"Error viewing scavenger hunt: {str(e)}")
        flash('Failed to load scavenger hunt.', 'error')
        return redirect(url_for('view_scenario'))

@login_required
def submit_task(task_id):
    """Handle task submission with comprehensive error handling"""
    try:
        task = ScavengerHuntTask.query.get_or_404(task_id)
        
        if 'photo' not in request.files:
            flash('No photo uploaded', 'error')
            return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))
        
        photo = request.files['photo']
        if not photo.filename:
            flash('No photo selected', 'error')
            return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))
        
        try:
            photo_path = save_photo(photo)
            if not photo_path:
                raise ValueError("Failed to save photo")
                
            is_verified, confidence_score = verify_photo_content(
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
                confidence_score=confidence_score,
                is_verified=is_verified
            )
            
            db.session.add(submission)
            db.session.commit()
            
            if is_verified:
                flash('Task completed successfully!', 'success')
            else:
                flash('Photo verification failed. Please try again.', 'warning')
                
        except Exception as e:
            logger.error(f"Error processing photo submission: {str(e)}")
            flash('Error processing photo submission. Please try again.', 'error')
            
        cleanup_old_photos()
        
        return redirect(url_for('scavenger_hunt', scenario_id=task.scenario_id))
        
    except Exception as e:
        logger.error(f"Error submitting task: {str(e)}")
        flash('Failed to submit task.', 'error')
        return redirect(url_for('view_scenario'))