from app import db

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

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    setting = db.Column(db.String(200))
    challenge = db.Column(db.String(200))
    goal = db.Column(db.String(200))
