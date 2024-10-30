from app import db
from datetime import datetime

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    # Appearance details
    height = db.Column(db.String(50))
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    style_preference = db.Column(db.String(100))
    signature_items = db.Column(db.String(200))
    
    # Background details
    childhood_story = db.Column(db.Text)
    family_relations = db.Column(db.Text)
    life_goals = db.Column(db.Text)
    achievements = db.Column(db.Text)
    
    # Personality details
    occupation = db.Column(db.String(100), nullable=False)
    communication_style = db.Column(db.String(200))
    challenge_handling = db.Column(db.String(200))
    hobbies = db.Column(db.String(200))
    quirks = db.Column(db.String(200))
    
    # Costume details
    costume = db.Column(db.Text)
    accessories = db.Column(db.Text)
    alternative_costumes = db.Column(db.Text)
    
    session_id = db.Column(db.String(100))
    template_id = db.Column(db.Integer, db.ForeignKey('character_template.id'), nullable=True)

class CharacterTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # Appearance templates
    height_options = db.Column(db.Text)  # Comma-separated options
    hair_color_options = db.Column(db.Text)
    eye_color_options = db.Column(db.Text)
    style_preference_options = db.Column(db.Text)
    signature_items_options = db.Column(db.Text)
    
    # Background templates
    childhood_story_templates = db.Column(db.Text)
    family_relations_templates = db.Column(db.Text)
    life_goals_templates = db.Column(db.Text)
    achievements_templates = db.Column(db.Text)
    
    # Personality templates
    occupation_options = db.Column(db.Text)
    communication_style_options = db.Column(db.Text)
    challenge_handling_options = db.Column(db.Text)
    hobbies_options = db.Column(db.Text)
    quirks_options = db.Column(db.Text)
    
    # Costume templates
    costume_options = db.Column(db.Text)
    accessories_options = db.Column(db.Text)
    alternative_costumes_options = db.Column(db.Text)
    
    session_id = db.Column(db.String(100))
    characters = db.relationship('Character', backref='template', lazy=True)

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    setting = db.Column(db.String(200))
    challenge = db.Column(db.String(200))
    goal = db.Column(db.String(200))
    points = db.Column(db.Integer, default=100)  # Points awarded for completing scenario

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))  # CSS class for the icon
    points_required = db.Column(db.Integer, default=0)
    scenarios_required = db.Column(db.Integer, default=0)
    session_id = db.Column(db.String(100))
    unlocked_at = db.Column(db.DateTime, default=None)

class ScenarioCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenario.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_earned = db.Column(db.Integer, default=0)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'))
    
    scenario = db.relationship('Scenario', backref='completions')
    character = db.relationship('Character', backref='completed_scenarios')
