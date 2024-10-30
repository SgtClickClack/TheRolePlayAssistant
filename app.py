import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text
from flask_session import Session

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "role-play-assistant-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["EXPLAIN_TEMPLATE_LOADING"] = True  # Enable template loading debug
app.config["DEBUG"] = True  # Enable debug mode
app.jinja_env.auto_reload = True

# Initialize Flask-Session
Session(app)

def verify_database():
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection successful")
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

# Initialize database and verify directories
with app.app_context():
    import models
    try:
        # Ensure upload directory exists
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        logger.info("Upload directory checked/created")
        
        if not verify_database():
            db.create_all()
            logger.info("Database tables created successfully")
        else:
            logger.info("Using existing database tables")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
