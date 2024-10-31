from flask import render_template, request, session, redirect, url_for, flash, jsonify, abort
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
        template_full_path = os.path.join('templates', template_path)
        exists = os.path.exists(template_full_path)
        if not exists:
            logger.error(f"Template not found: {template_path} (full path: {template_full_path})")
        return exists
    except Exception as e:
        logger.error(f"Error checking template {template_path}: {str(e)}")
        return False

def render_template_safe(template_name, **context):
    """Safe template rendering with error handling"""
    try:
        if not verify_template_exists(template_name):
            logger.error(f"Template {template_name} not found")
            return render_template('500.html', error_id=str(uuid.uuid4()))
        return render_template(template_name, **context)
    except jinja2.exceptions.TemplateNotFound as e:
        logger.error(f"Template not found error: {str(e)}")
        return render_template('500.html', error_id=str(uuid.uuid4()))
    except Exception as e:
        logger.error(f"Template rendering error: {str(e)}\n{traceback.format_exc()}")
        return render_template('500.html', error_id=str(uuid.uuid4()))

def register_routes(app):
    """Register all routes with the Flask app"""
    
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
        db.session.rollback()
        error_id = str(uuid.uuid4())
        error_details = f"Internal server error [{error_id}]: {str(error)}\n{traceback.format_exc()}"
        logger.error(error_details)
        
        if current_user.is_authenticated:
            user_info = f"User ID: {current_user.id}, Username: {current_user.username}"
            logger.error(f"Error occurred for authenticated user: {user_info}")
        
        return render_template_safe('500.html', error_id=error_id), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"Forbidden access attempt: {request.url}\nUser: {current_user if current_user.is_authenticated else 'Anonymous'}")
        return render_template_safe('403.html'), 403

    @app.route('/')
    def index():
        try:
            templates = CharacterTemplate.query.all() if current_user.is_authenticated else []
            return render_template_safe('index.html', templates=templates)
        except Exception as e:
            logger.error(f"Error in index route: {str(e)}\n{traceback.format_exc()}")
            db.session.rollback()
            return internal_error(e)

    @app.route('/create_template', methods=['GET', 'POST'])
    @login_required
    def create_template():
        """Handle character template creation"""
        try:
            if request.method == 'POST':
                template = CharacterTemplate(
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    height_options=request.form.get('height_options'),
                    hair_color_options=request.form.get('hair_color_options'),
                    eye_color_options=request.form.get('eye_color_options'),
                    style_preference_options=request.form.get('style_preference_options'),
                    signature_items_options=request.form.get('signature_items_options'),
                    childhood_story_templates=request.form.get('childhood_story_templates'),
                    family_relations_templates=request.form.get('family_relations_templates'),
                    occupation_options=request.form.get('occupation_options'),
                    communication_style_options=request.form.get('communication_style_options'),
                    hobbies_options=request.form.get('hobbies_options'),
                    quirks_options=request.form.get('quirks_options'),
                    costume_options=request.form.get('costume_options'),
                    accessories_options=request.form.get('accessories_options'),
                    alternative_costumes_options=request.form.get('alternative_costumes_options'),
                    user_id=current_user.id
                )
                db.session.add(template)
                db.session.commit()
                flash('Template created successfully!', 'success')
                return redirect(url_for('index'))
                
            return render_template_safe('create_template.html')
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}\n{traceback.format_exc()}")
            db.session.rollback()
            flash('An error occurred while creating the template', 'error')
            return redirect(url_for('index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
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
                return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                db.session.rollback()
                flash('An error occurred during registration', 'error')
                
        return render_template_safe('auth/register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/scavenger_hunt/<int:task_id>')
    @login_required
    def view_scavenger_hunt(task_id):
        try:
            task = ScavengerHuntTask.query.get(task_id)
            if not task:
                logger.warning(f"Scavenger hunt task not found: {task_id}")
                flash('Scavenger hunt task not found', 'error')
                return redirect(url_for('index'))

            scenario = Scenario.query.get(task.scenario_id)
            if not scenario:
                logger.error(f"Scenario not found for task: {task_id}")
                return internal_error("Associated scenario not found")

            submissions = TaskSubmission.query.filter_by(
                task_id=task_id,
                user_id=current_user.id
            ).order_by(TaskSubmission.submitted_at.desc()).all()

            return render_template_safe('scavenger_hunt.html', 
                                   task=task,
                                   scenario=scenario,
                                   submissions=submissions)
        except Exception as e:
            logger.error(f"Error viewing scavenger hunt: {str(e)}\n{traceback.format_exc()}")
            return internal_error(e)

    @app.route('/character/<int:char_id>')
    @login_required
    def view_character(char_id):
        try:
            character = Character.query.get_or_404(char_id)
            if character.user_id != current_user.id:
                return forbidden_error(None)
            return render_template_safe('character.html', character=character)
        except Exception as e:
            logger.error(f"Error viewing character: {str(e)}\n{traceback.format_exc()}")
            return internal_error(e)

    @app.route('/profile')
    @login_required
    def profile():
        try:
            return render_template_safe('auth/profile.html')
        except Exception as e:
            logger.error(f"Error viewing profile: {str(e)}\n{traceback.format_exc()}")
            return internal_error(e)

    @app.route('/create_character', methods=['GET', 'POST'])
    @login_required
    def create_new_character():
        try:
            template_id = request.form.get('template_id')
            if template_id:
                template = CharacterTemplate.query.get_or_404(template_id)
                character_data = generate_character_from_template(template)
            else:
                character_data = create_character_data()
                
            character = Character(**character_data)
            character.user_id = current_user.id
            db.session.add(character)
            db.session.commit()
            
            flash('Character created successfully!', 'success')
            return redirect(url_for('view_character', char_id=character.id))
        except Exception as e:
            logger.error(f"Error creating character: {str(e)}\n{traceback.format_exc()}")
            db.session.rollback()
            flash('An error occurred while creating the character', 'error')
            return redirect(url_for('index'))

    @app.route('/scenario')
    @login_required
    def view_scenario():
        try:
            scenario = get_random_scenario()
            if not scenario:
                flash('No scenarios available at the moment', 'info')
                return redirect(url_for('index'))
                
            completion = ScenarioCompletion.query.filter_by(
                scenario_id=scenario['id'],
                user_id=current_user.id
            ).first()
            
            characters = Character.query.filter_by(user_id=current_user.id).all()
            achievements = Achievement.query.filter_by(user_id=current_user.id).all()
            total_points = sum(c.points_earned for c in ScenarioCompletion.query.filter_by(user_id=current_user.id).all())
            
            return render_template_safe('scenario.html',
                                   scenario=scenario,
                                   is_completed=bool(completion),
                                   completion=completion,
                                   characters=characters,
                                   achievements=achievements,
                                   total_points=total_points)
        except Exception as e:
            logger.error(f"Error viewing scenario: {str(e)}\n{traceback.format_exc()}")
            return internal_error(e)

    logger.info("All routes registered successfully")
    return app
