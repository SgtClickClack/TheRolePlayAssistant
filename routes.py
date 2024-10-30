from flask import render_template, request, session, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion, User, ScavengerHuntTask, TaskSubmission
from utils import generate_character as create_character_data, get_random_scenario, generate_character_from_template
from photo_verification import verify_photo_content, save_photo, allowed_file
import uuid
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    try:
        logger.info("Processing index route request")
        
        templates = []
        if current_user.is_authenticated:
            logger.info(f"Fetching templates for user: {current_user.id}")
            templates = CharacterTemplate.query.filter_by(user_id=current_user.id).all()
            logger.debug(f"Found {len(templates)} templates for user")
        
        logger.info("Rendering index template")
        return render_template('index.html', templates=templates)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}\n{traceback.format_exc()}")
        return render_template('500.html'), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please provide both email and password', 'error')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                logger.info(f"User {email} logged in successfully")
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            
            flash('Invalid email or password', 'error')
        return render_template('auth/login.html')
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return render_template('auth/register.html')
                
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('auth/register.html')
                
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            logger.info(f"New user registered: {email}")
            return redirect(url_for('index'))
            
        return render_template('auth/register.html')
    except Exception as e:
        logger.error(f"Error in registration route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in logout route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/profile')
@login_required
def profile():
    try:
        return render_template('auth/profile.html')
    except Exception as e:
        logger.error(f"Error in profile route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/create_template', methods=['GET', 'POST'])
@login_required
def create_template():
    try:
        if request.method == 'POST':
            template = CharacterTemplate(
                name=request.form['name'],
                description=request.form['description'],
                user_id=current_user.id,
                height_options=request.form.get('height_options'),
                hair_color_options=request.form.get('hair_color_options'),
                eye_color_options=request.form.get('eye_color_options'),
                style_preference_options=request.form.get('style_preference_options'),
                signature_items_options=request.form.get('signature_items_options'),
                occupation_options=request.form.get('occupation_options'),
                communication_style_options=request.form.get('communication_style_options'),
                hobbies_options=request.form.get('hobbies_options'),
                quirks_options=request.form.get('quirks_options'),
                costume_options=request.form.get('costume_options'),
                accessories_options=request.form.get('accessories_options'),
                alternative_costumes_options=request.form.get('alternative_costumes_options')
            )
            db.session.add(template)
            db.session.commit()
            flash('Template created successfully!', 'success')
            return redirect(url_for('index'))
        return render_template('create_template.html')
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return render_template('500.html'), 500

@app.route('/scavenger_hunt/<int:id>')
@login_required
def scavenger_hunt(id):
    try:
        logger.info(f"Fetching scavenger hunt scenario {id}")
        scenario = Scenario.query.get_or_404(id)
        
        tasks = ScavengerHuntTask.query.filter_by(scenario_id=id).all()
        logger.debug(f"Found {len(tasks)} tasks for scenario {id}")
        
        for task in tasks:
            task.submissions = TaskSubmission.query.filter_by(
                task_id=task.id,
                user_id=current_user.id
            ).all()
        
        return render_template('scavenger_hunt.html',
                             scenario=scenario,
                             tasks=tasks)
    except Exception as e:
        logger.error(f"Error in scavenger hunt route: {str(e)}\n{traceback.format_exc()}")
        return render_template('500.html'), 500

@app.route('/submit_task/<int:task_id>', methods=['POST'])
@login_required
def submit_task(task_id):
    try:
        logger.info(f"Processing task submission for task {task_id}")
        task = ScavengerHuntTask.query.get_or_404(task_id)
        
        if 'photo' not in request.files:
            flash('No photo uploaded', 'error')
            return redirect(url_for('scavenger_hunt', id=task.scenario_id))
            
        photo = request.files['photo']
        if not photo or not allowed_file(photo.filename):
            flash('Invalid file type', 'error')
            return redirect(url_for('scavenger_hunt', id=task.scenario_id))
            
        try:
            photo_path = save_photo(photo)
            logger.info(f"Photo saved at {photo_path}")
            
            is_verified, confidence = verify_photo_content(
                photo_path,
                task.required_objects,
                task.object_confidence,
                task.required_pose,
                task.required_location
            )
            
            submission = TaskSubmission(
                task_id=task_id,
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
                flash('Photo verification failed. Please try again.', 'error')
                
        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}")
            flash('Error processing photo', 'error')
            
        return redirect(url_for('scavenger_hunt', id=task.scenario_id))
        
    except Exception as e:
        logger.error(f"Error in task submission: {str(e)}\n{traceback.format_exc()}")
        return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error: {request.path}")
    return render_template('404.html', 
                         error_path=request.path,
                         suggested_paths=[
                             ('Home', url_for('index')),
                             ('Profile', url_for('profile')),
                             ('Scenarios', url_for('view_scenario'))
                         ]), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}\n{traceback.format_exc()}")
    db.session.rollback()
    return render_template('500.html'), 500

@app.before_request
def before_request():
    """Log all requests"""
    logger.info(f"Processing request: {request.method} {request.path}")
    if not session.get('session_id'):
        session['session_id'] = str(uuid.uuid4())