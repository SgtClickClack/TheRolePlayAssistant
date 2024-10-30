import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text

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
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        
        # Check if tables exist by querying the information schema
        result = db.session.execute(text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user')"
        ))
        tables_exist = result.scalar()
        
        if not tables_exist:
            logger.info("Tables do not exist. Creating database schema...")
            return False
        
        logger.info("Database schema verification successful")
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
    try:
        if not verify_database():
            db.create_all()  # Only create tables if they don't exist
            logger.info("Database tables created successfully")
        else:
            logger.info("Using existing database tables")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
