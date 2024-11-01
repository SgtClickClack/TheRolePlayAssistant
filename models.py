from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    gender = db.Column(db.String(10), nullable=True)  # Options: 'male', 'female', 'other'
    spiciness_level = db.Column(db.Integer, default=1)  # 1: Family-friendly, 2: Mild, 3: Spicy
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    characters = db.relationship('Character', backref='user', lazy=True)
    templates = db.relationship('CharacterTemplate', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.String(50))
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    style_preference = db.Column(db.String(100))
    signature_items = db.Column(db.String(200))
    childhood_story = db.Column(db.Text)
    family_relations = db.Column(db.Text)
    life_goals = db.Column(db.Text)
    achievements = db.Column(db.Text)
    occupation = db.Column(db.String(100), nullable=False)
    communication_style = db.Column(db.String(200))
    challenge_handling = db.Column(db.String(200))
    hobbies = db.Column(db.String(200))
    quirks = db.Column(db.String(200))
    costume = db.Column(db.Text)
    accessories = db.Column(db.Text)
    alternative_costumes = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    template_id = db.Column(db.Integer, db.ForeignKey('character_template.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class CharacterTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    height_options = db.Column(db.Text)
    hair_color_options = db.Column(db.Text)
    eye_color_options = db.Column(db.Text)
    style_preference_options = db.Column(db.Text)
    signature_items_options = db.Column(db.Text)
    childhood_story_templates = db.Column(db.Text)
    family_relations_templates = db.Column(db.Text)
    life_goals_templates = db.Column(db.Text)
    achievements_templates = db.Column(db.Text)
    occupation_options = db.Column(db.Text)
    communication_style_options = db.Column(db.Text)
    challenge_handling_options = db.Column(db.Text)
    hobbies_options = db.Column(db.Text)
    quirks_options = db.Column(db.Text)
    costume_options = db.Column(db.Text)
    accessories_options = db.Column(db.Text)
    alternative_costumes_options = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    characters = db.relationship('Character', backref='template', lazy=True)

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    setting = db.Column(db.String(200))
    challenge = db.Column(db.String(200))
    goal = db.Column(db.String(200))
    points = db.Column(db.Integer, default=100)
    tasks = db.relationship('ScavengerHuntTask', backref='scenario', lazy=True)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))
    points_required = db.Column(db.Integer, default=0)
    scenarios_required = db.Column(db.Integer, default=0)
    session_id = db.Column(db.String(100))
    unlocked_at = db.Column(db.DateTime, default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class ScenarioCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_earned = db.Column(db.Integer, default=0)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    scenario = db.relationship('Scenario', backref='completions')
    character = db.relationship('Character', backref='completed_scenarios')

class ScavengerHuntTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_objects = db.Column(db.JSON, nullable=False)
    required_pose = db.Column(db.String(100))
    required_location = db.Column(db.String(200))
    object_confidence = db.Column(db.Float, default=0.7)
    points = db.Column(db.Integer, default=50)
    time_limit = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submissions = db.relationship('TaskSubmission', backref='task', lazy=True)

class TaskSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('scavenger_hunt_task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_path = db.Column(db.String(255), nullable=False)
    confidence_score = db.Column(db.Float)
    is_verified = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)
    location_data = db.Column(db.JSON)
    pose_data = db.Column(db.JSON)