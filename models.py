from app import db

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    personality = db.Column(db.String(200))
    interests = db.Column(db.String(200))
    costume = db.Column(db.String(200))
    special_ability = db.Column(db.String(200))
    session_id = db.Column(db.String(100))

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    setting = db.Column(db.String(200))
    challenge = db.Column(db.String(200))
    goal = db.Column(db.String(200))
