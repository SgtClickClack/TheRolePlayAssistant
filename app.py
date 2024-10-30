import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "family-friendly-rpg-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

def verify_database():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        logger.info("Database connection successful")
        
        # Get all table names
        table_names = db.session.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'').fetchall()
        logger.info(f"Existing tables: {[table[0] for table in table_names]}")
        
        return True
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    import models
    if verify_database():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create tables with the new schema
        logger.info("Database tables created successfully")
    else:
        logger.error("Failed to verify database connection")
