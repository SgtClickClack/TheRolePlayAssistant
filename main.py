from flask import render_template, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion, User
from utils import generate_character as create_character_data, get_random_scenario, generate_character_from_template
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ACHIEVEMENTS = [
    {
        "name": "Adventurer Novice",
        "description": "Complete your first scenario",
        "icon": "bi-stars",
        "scenarios_required": 1,
        "points_required": 100
    },
    {
        "name": "Seasoned Explorer",
        "description": "Complete 5 scenarios",
        "icon": "bi-trophy",
        "scenarios_required": 5,
        "points_required": 500
    },
    {
        "name": "Master Storyteller",
        "description": "Earn 1000 points from completed scenarios",
        "icon": "bi-book",
        "scenarios_required": 0,
        "points_required": 1000
    }
]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.debug(f"Already authenticated user {current_user.id} attempting to access login page")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            logger.warning("Login attempt with missing email or password")
            flash('Both email and password are required', 'error')
            return render_template('auth/login.html')
            
        try:
            user = User.query.filter_by(email=email).first()
            logger.debug(f"Login attempt for email: {email}")
            
            if user is None:
                logger.warning(f"Login attempt for non-existent email: {email}")
                flash('No account found with this email address', 'error')
                return render_template('auth/login.html')
                
            if not user.check_password(password):
                logger.warning(f"Failed login attempt for user {user.id}: incorrect password")
                flash('Incorrect password', 'error')
                return render_template('auth/login.html')
                
            login_user(user)
            logger.info(f"Successful login for user {user.id}")
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
            
        except Exception as e:
            logger.error(f"Error during login process: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('auth/login.html')
            
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        logger.debug(f"Authenticated user {current_user.id} attempting to access register page")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not all([username, email, password, confirm_password]):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                logger.warning(f"Password mismatch during registration for username: {username}")
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))
                
            if User.query.filter_by(username=username).first():
                logger.warning(f"Registration attempt with existing username: {username}")
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
                
            if User.query.filter_by(email=email).first():
                logger.warning(f"Registration attempt with existing email: {email}")
                flash('Email already registered', 'error')
                return redirect(url_for('register'))
                
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Successfully registered new user: {user.id}")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Error during registration process: {str(e)}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
        
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    logger.info(f"User {user_id} logged out")
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    logger.debug(f"User {current_user.id} accessing profile page")
    return render_template('auth/profile.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        gender = request.form.get('gender')
        spiciness_level = request.form.get('spiciness_level', type=int)
        
        if gender not in ['male', 'female', 'other']:
            logger.warning(f"Invalid gender selection for user {current_user.id}: {gender}")
            flash('Invalid gender selection', 'error')
            return redirect(url_for('profile'))
            
        if spiciness_level not in [1, 2, 3]:
            logger.warning(f"Invalid spiciness level for user {current_user.id}: {spiciness_level}")
            flash('Invalid spiciness level selection', 'error')
            return redirect(url_for('profile'))
        
        current_user.gender = gender
        current_user.spiciness_level = spiciness_level
        db.session.commit()
        
        logger.info(f"Profile updated successfully for user {current_user.id}")
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        flash('An error occurred while updating profile', 'error')
        return redirect(url_for('profile'))

def init_achievements(user_id):
    try:
        for achievement_data in ACHIEVEMENTS:
            achievement = Achievement.query.filter_by(
                user_id=user_id,
                name=achievement_data['name']
            ).first()
            
            if not achievement:
                achievement = Achievement(
                    user_id=user_id,
                    **achievement_data
                )
                db.session.add(achievement)
        db.session.commit()
        logger.debug(f"Initialized achievements for user {user_id}")
    except Exception as e:
        logger.error(f"Error initializing achievements for user {user_id}: {str(e)}")
        db.session.rollback()

@app.route('/')
def index():
    if current_user.is_authenticated:
        logger.debug(f"Authenticated user {current_user.id} accessing index page")
        init_achievements(current_user.id)
        templates = CharacterTemplate.query.filter_by(user_id=current_user.id).all()
    else:
        logger.debug("Anonymous user accessing index page")
        templates = []
    return render_template('index.html', templates=templates)

@app.route('/generate_character', methods=['POST'])
@login_required
def create_new_character():
    try:
        template_id = request.form.get('template_id')
        if template_id:
            template = CharacterTemplate.query.get_or_404(template_id)
            char_data = generate_character_from_template(template)
            logger.debug(f"Generating character from template {template_id} for user {current_user.id}")
        else:
            char_data = create_character_data()
            logger.debug(f"Generating random character for user {current_user.id}")
        
        character = Character(
            user_id=current_user.id,
            template_id=template_id,
            **char_data
        )
        db.session.add(character)
        db.session.commit()
        logger.info(f"Successfully created character {character.id} for user {current_user.id}")
        return redirect(url_for('view_character', char_id=character.id))
    except Exception as e:
        logger.error(f"Error generating character for user {current_user.id}: {str(e)}")
        flash("An error occurred while generating your character. Please try again.", "error")
        return redirect(url_for('index'))

@app.route('/character/<int:char_id>')
@login_required
def view_character(char_id):
    try:
        character = Character.query.get_or_404(char_id)
        if character.user_id != current_user.id:
            logger.warning(f"User {current_user.id} attempted to view character {char_id} belonging to user {character.user_id}")
            flash("You don't have permission to view this character.", "error")
            return redirect(url_for('index'))
        scenario = get_random_scenario()
        logger.debug(f"User {current_user.id} viewing character {char_id}")
        return render_template('character.html', character=character, scenario=scenario)
    except Exception as e:
        logger.error(f"Error viewing character {char_id}: {str(e)}")
        flash("An error occurred while loading the character.", "error")
        return redirect(url_for('index'))

@app.route('/create_template', methods=['GET', 'POST'])
@login_required
def create_template():
    if request.method == 'POST':
        try:
            template = CharacterTemplate(
                user_id=current_user.id,
                name=request.form['name'],
                description=request.form.get('description', ''),
                height_options=request.form.get('height_options', ''),
                hair_color_options=request.form.get('hair_color_options', ''),
                eye_color_options=request.form.get('eye_color_options', ''),
                style_preference_options=request.form.get('style_preference_options', ''),
                signature_items_options=request.form.get('signature_items_options', ''),
                childhood_story_templates=request.form.get('childhood_story_templates', ''),
                family_relations_templates=request.form.get('family_relations_templates', ''),
                life_goals_templates=request.form.get('life_goals_templates', ''),
                achievements_templates=request.form.get('achievements_templates', ''),
                occupation_options=request.form.get('occupation_options', ''),
                communication_style_options=request.form.get('communication_style_options', ''),
                challenge_handling_options=request.form.get('challenge_handling_options', ''),
                hobbies_options=request.form.get('hobbies_options', ''),
                quirks_options=request.form.get('quirks_options', ''),
                costume_options=request.form.get('costume_options', ''),
                accessories_options=request.form.get('accessories_options', ''),
                alternative_costumes_options=request.form.get('alternative_costumes_options', '')
            )
            db.session.add(template)
            db.session.commit()
            logger.info(f"Created template {template.id} for user {current_user.id}")
            flash('Template created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error creating template for user {current_user.id}: {str(e)}")
            flash("An error occurred while creating the template. Please try again.", "error")
            return redirect(url_for('create_template'))
    return render_template('create_template.html')

@app.route('/scenario')
@login_required
def view_scenario():
    try:
        characters = Character.query.filter_by(user_id=current_user.id).all()
        scenario = get_random_scenario()
        
        db_scenario = Scenario.query.filter_by(
            title=scenario['title'],
            description=scenario['description']
        ).first()
        
        if not db_scenario:
            db_scenario = Scenario(
                title=scenario['title'],
                description=scenario['description'],
                setting=scenario['setting'],
                challenge=scenario['challenge'],
                goal=scenario['goal'],
                points=100
            )
            db.session.add(db_scenario)
            db.session.commit()
            logger.debug(f"Created new scenario: {db_scenario.id}")
        
        completion = ScenarioCompletion.query.filter_by(
            user_id=current_user.id,
            scenario_id=db_scenario.id
        ).first()
        
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        total_points = db.session.query(db.func.sum(ScenarioCompletion.points_earned))\
            .filter_by(user_id=current_user.id).scalar() or 0
        
        logger.debug(f"User {current_user.id} viewing scenario {db_scenario.id}")
        return render_template('scenario.html', 
                             characters=characters, 
                             scenario=db_scenario,
                             is_completed=bool(completion),
                             completion=completion,
                             achievements=achievements,
                             total_points=total_points)
    except Exception as e:
        logger.error(f"Error viewing scenario for user {current_user.id}: {str(e)}")
        flash("An error occurred while loading the scenario.", "error")
        return redirect(url_for('index'))

@app.route('/complete_scenario/<int:scenario_id>', methods=['POST'])
@login_required
def complete_scenario(scenario_id):
    try:
        scenario = Scenario.query.get_or_404(scenario_id)
        
        existing_completion = ScenarioCompletion.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_id
        ).first()
        
        if existing_completion:
            logger.warning(f"User {current_user.id} attempted to complete already completed scenario {scenario_id}")
            flash('Scenario already completed!', 'warning')
            return redirect(url_for('view_scenario'))
        
        completion = ScenarioCompletion(
            user_id=current_user.id,
            scenario_id=scenario_id,
            points_earned=scenario.points
        )
        db.session.add(completion)
        
        total_completions = ScenarioCompletion.query.filter_by(
            user_id=current_user.id
        ).count() + 1
        
        total_points = db.session.query(db.func.sum(ScenarioCompletion.points_earned))\
            .filter_by(user_id=current_user.id).scalar() or 0
        total_points += scenario.points
        
        achievements = Achievement.query.filter_by(
            user_id=current_user.id,
            unlocked_at=None
        ).all()
        
        for achievement in achievements:
            if (achievement.scenarios_required > 0 and total_completions >= achievement.scenarios_required) or \
               (achievement.points_required > 0 and total_points >= achievement.points_required):
                achievement.unlocked_at = datetime.utcnow()
                logger.info(f"User {current_user.id} unlocked achievement: {achievement.name}")
                flash(f'Achievement Unlocked: {achievement.name}!', 'success')
        
        db.session.commit()
        logger.info(f"User {current_user.id} completed scenario {scenario_id}")
        flash('Scenario completed successfully!', 'success')
        return redirect(url_for('view_scenario'))
    except Exception as e:
        logger.error(f"Error completing scenario {scenario_id} for user {current_user.id}: {str(e)}")
        db.session.rollback()
        flash("An error occurred while completing the scenario.", "error")
        return redirect(url_for('view_scenario'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)