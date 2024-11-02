import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from sqlalchemy import text
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import time

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

def verify_database_connection(app, max_retries=5, retry_delay=2):
    """Verify database connection with retries"""
    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                logger.info("Database connection verified successfully")
                return True
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return False

def verify_template_directory(app):
    """Verify template directory exists and is readable"""
    try:
        if not os.path.exists(app.template_folder):
            logger.error(f"Template folder not found: {app.template_folder}")
            return False
        if not os.access(app.template_folder, os.R_OK):
            logger.error(f"Template folder not readable: {app.template_folder}")
            return False
        logger.info("Template directory verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying template directory: {str(e)}")
        return False

def verify_static_directory(app):
    """Verify static directory exists and is readable"""
    try:
        if not os.path.exists(app.static_folder):
            logger.error(f"Static folder not found: {app.static_folder}")
            return False
        if not os.access(app.static_folder, os.R_OK):
            logger.error(f"Static folder not readable: {app.static_folder}")
            return False
        logger.info("Static directory verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying static directory: {str(e)}")
        return False

def create_app():
    """Create and configure the Flask application with improved error handling"""
    try:
        # Create Flask app with explicit template and static folders
        app = Flask(__name__, 
                  template_folder='templates',
                  static_folder='static',
                  static_url_path='/static')
        
        # Configure app with error handling for environment variables
        app.config.update(
            SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
            SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
            SQLALCHEMY_ENGINE_OPTIONS={
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "pool_timeout": 20,
                "max_overflow": 5,
                "pool_size": 5
            },
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SESSION_TYPE="filesystem",
            TEMPLATES_AUTO_RELOAD=True,
            DEBUG=True,
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
            SEND_FILE_MAX_AGE_DEFAULT=0,
            EXPLAIN_TEMPLATE_LOADING=True,
            JSON_AS_ASCII=False,
            USE_RELOADER=False,
            MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
        )
        
        # Verify required directories exist
        required_dirs = ['templates', 'static', 'static/uploads', 'static/css', 'static/js', 'flask_session']
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
        
        # Verify template and static directories
        if not verify_template_directory(app):
            raise RuntimeError("Failed to verify template directory")
        if not verify_static_directory(app):
            raise RuntimeError("Failed to verify static directory")
        
        # Initialize extensions with error handling
        try:
            db.init_app(app)
            csrf.init_app(app)
            Session(app)
            
            # Initialize login manager
            login_manager.init_app(app)
            login_manager.login_view = 'login'
            login_manager.login_message_category = 'info'
            login_manager.needs_refresh_message_category = 'info'
            
            logger.info("Extensions initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize extensions: {str(e)}")
            raise
        
        # Import models and routes within app context
        with app.app_context():
            from models import User
            from routes import register_routes, render_template_safe
            
            # Create database tables with retry mechanism
            try:
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Failed to create database tables: {str(e)}")
                raise
            
            # Register routes
            try:
                register_routes(app)
                logger.info("Routes registered successfully")
            except Exception as e:
                logger.error(f"Failed to register routes: {str(e)}")
                raise
            
            # Verify database connection with retries
            if not verify_database_connection(app):
                raise RuntimeError("Failed to verify database connection")
        
        # Register error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template_safe('404.html'), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template_safe('500.html'), 500
            
        logger.info("Application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise

# User loader callback with error handling
@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {str(e)}")
        return None
