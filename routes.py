from flask import render_template, request, session, redirect, url_for, flash, jsonify, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion, User, ScavengerHuntTask, TaskSubmission
from utils import generate_character as create_character_data, get_random_scenario, generate_character_from_template
from photo_verification import verify_photo_content, save_photo, allowed_file
import uuid
from datetime import datetime, timedelta
import logging
import traceback
import os
import jinja2

logger = logging.getLogger(__name__)

def verify_template_exists(template_path):
    """Verify if a template file exists with improved error handling"""
    try:
        template_loader = jinja2.FileSystemLoader('templates')
        env = jinja2.Environment(loader=template_loader)
        env.get_template(template_path)
        return True
    except jinja2.TemplateNotFound:
        logger.error(f"Template not found: {template_path}")
        return False
    except Exception as e:
        logger.error(f"Error verifying template {template_path}: {str(e)}")
        return False

def render_template_safe(template_name, **context):
    """Safe template rendering with error handling and logging"""
    try:
        if not verify_template_exists(template_name):
            error_id = str(uuid.uuid4())
            logger.error(f"Template {template_name} not found. Error ID: {error_id}")
            return render_template('500.html', 
                                error_id=error_id,
                                error_message="Template not found"), 500
                                
        # Add common context variables
        context.update({
            'error_id': str(uuid.uuid4()),
            'error_path': request.path
        })
        
        return render_template(template_name, **context)
    except Exception as e:
        error_id = str(uuid.uuid4())
        logger.error(f"Template rendering error: {str(e)}\n{traceback.format_exc()} Error ID: {error_id}")
        return render_template('500.html', error_id=error_id), 500

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.before_request
    def before_request():
        """Pre-request processing"""
        logger.debug(f"Incoming request: {request.method} {request.path}")
        
    @app.after_request
    def after_request(response):
        """Post-request processing"""
        logger.debug(f"Response status: {response.status_code}")
        if response.status_code == 404:
            logger.warning(f"404 error for path: {request.path}")
        return response
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Enhanced 404 error handler with detailed logging"""
        error_details = {
            'url': request.url,
            'method': request.method,
            'referrer': request.referrer,
            'user_agent': str(request.user_agent),
            'user': current_user.username if current_user.is_authenticated else 'Anonymous'
        }
        logger.warning(f"404 Error - Page not found: {error_details}")
        return render_template_safe('404.html', 
                               error_path=request.path,
                               referrer=request.referrer), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Enhanced 500 error handler with detailed logging"""
        db.session.rollback()
        error_id = str(uuid.uuid4())
        error_details = f"Internal server error [{error_id}]: {str(error)}\n{traceback.format_exc()}"
        logger.error(error_details)
        return render_template_safe('500.html', error_id=error_id), 500

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files with proper error handling"""
        try:
            logger.debug(f"Serving static file: {filename}")
            if not app.static_folder:
                logger.error("Static folder not configured")
                abort(500)
                
            if not os.path.exists(os.path.join(app.static_folder, filename)):
                logger.warning(f"Static file not found: {filename}")
                abort(404)
                
            return send_from_directory(app.static_folder, filename)
        except Exception as e:
            logger.error(f"Error serving static file {filename}: {str(e)}")
            abort(404)

    @app.route('/')
    def index():
        """Home page route with enhanced error handling"""
        try:
            logger.debug("Rendering index page")
            templates = CharacterTemplate.query.all() if current_user.is_authenticated else []
            return render_template_safe('index.html', templates=templates)
        except Exception as e:
            logger.error(f"Error in index route: {str(e)}\n{traceback.format_exc()}")
            return render_template_safe('500.html', error_id=str(uuid.uuid4())), 500
            
    @app.route('/view_scenario')
    @login_required
    def view_scenario():
        """View current scenario route"""
        try:
            # Get or create a new scenario
            scenario = Scenario.query.first()
            if not scenario:
                scenario_data = get_random_scenario()
                scenario = Scenario(**scenario_data)
                db.session.add(scenario)
                db.session.commit()
            
            # Get user's characters
            characters = Character.query.filter_by(user_id=current_user.id).all()
            
            # Get completion status
            completion = ScenarioCompletion.query.filter_by(
                scenario_id=scenario.id,
                user_id=current_user.id
            ).first()
            
            # Get achievements
            achievements = Achievement.query.filter_by(user_id=current_user.id).all()
            
            # Calculate total points
            total_points = sum(completion.points_earned for completion in 
                             ScenarioCompletion.query.filter_by(user_id=current_user.id).all())
            
            return render_template_safe('scenario.html',
                                   scenario=scenario,
                                   characters=characters,
                                   is_completed=bool(completion),
                                   completion=completion,
                                   achievements=achievements,
                                   total_points=total_points)
        except Exception as e:
            logger.error(f"Error viewing scenario: {str(e)}")
            return render_template_safe('500.html', error_id=str(uuid.uuid4())), 500

    @app.route('/scavenger_hunt/<int:scenario_id>')
    @login_required
    def view_scavenger_hunt(scenario_id):
        """View specific scavenger hunt"""
        try:
            scenario = Scenario.query.get_or_404(scenario_id)
            tasks = ScavengerHuntTask.query.filter_by(scenario_id=scenario_id).all()
            
            # Load submissions for each task
            for task in tasks:
                task.submissions = TaskSubmission.query.filter_by(
                    task_id=task.id,
                    user_id=current_user.id
                ).order_by(TaskSubmission.submitted_at.desc()).all()
            
            return render_template_safe('scavenger_hunt.html',
                                   scenario=scenario,
                                   tasks=tasks)
        except Exception as e:
            logger.error(f"Error viewing scavenger hunt {scenario_id}: {str(e)}")
            return render_template_safe('500.html', error_id=str(uuid.uuid4())), 500

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login route with enhanced error handling"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            try:
                email = request.form.get('email')
                password = request.form.get('password')
                remember = bool(request.form.get('remember'))
                
                user = User.query.filter_by(email=email).first()
                if user and user.check_password(password):
                    login_user(user, remember=remember)
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('index'))
                flash('Invalid email or password', 'error')
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                flash('An error occurred during login', 'error')
                
        return render_template_safe('auth/login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration route with enhanced error handling"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                
                if User.query.filter_by(username=username).first():
                    flash('Username already exists', 'error')
                    return render_template_safe('auth/register.html')
                    
                if User.query.filter_by(email=email).first():
                    flash('Email already registered', 'error')
                    return render_template_safe('auth/register.html')
                
                user = User(username=username, email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                login_user(user)
                flash('Registration successful!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                db.session.rollback()
                flash('An error occurred during registration', 'error')
                
        return render_template_safe('auth/register.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Logout route"""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))

    @app.route('/profile')
    @login_required
    def profile():
        """User profile route"""
        return render_template_safe('auth/profile.html')

    logger.info("All routes registered successfully")
    return app
