import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import socket

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flask_debug.log')
    ]
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    try:
        # Get absolute paths for template and static directories
        current_dir = os.path.abspath(os.path.dirname(__file__))
        template_dir = os.path.join(current_dir, 'templates')
        static_dir = os.path.join(current_dir, 'static')
        
        # Verify directories exist before creating app
        for directory in [template_dir, static_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
        
        # Create Flask app with explicit template and static folders
        app = Flask(__name__, 
                    template_folder=template_dir,
                    static_folder=static_dir,
                    static_url_path='/static')
        
        # Configure app with debug logging
        app.config.update(
            SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
            SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
            SQLALCHEMY_ENGINE_OPTIONS={
                "pool_recycle": 300,
                "pool_pre_ping": True,
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
            SERVER_NAME=None
        )
        
        # Create required directories
        required_dirs = [
            template_dir,
            static_dir,
            os.path.join(static_dir, 'uploads'),
            os.path.join(static_dir, 'css'),
            os.path.join(static_dir, 'js'),
            'flask_session'
        ]
        
        for directory in required_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {str(e)}")
                raise RuntimeError(f"Failed to initialize application directories: {str(e)}")
        
        # Initialize extensions with proper order
        db.init_app(app)
        csrf.init_app(app)
        Session(app)
        
        # Initialize login manager after other extensions
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        
        with app.app_context():
            try:
                # Import models before creating tables
                from models import User, Character, CharacterTemplate, Scenario
                
                # Create database tables
                db.create_all()
                logger.info("Database tables created successfully")
                
                # Import and register routes
                from routes import register_routes
                app = register_routes(app)
                logger.info("Routes registered successfully")
                
                # Verify database connection
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                logger.info("Database connection verified")
                
                # Log configuration details
                logger.debug(f"App config: {app.config}")
                logger.info(f"Template folder: {app.template_folder}")
                logger.info(f"Static folder: {app.static_folder}")
                logger.info(f"Static URL path: {app.static_url_path}")
                
            except Exception as e:
                logger.error(f"Application initialization failed: {str(e)}")
                raise
        
        return app
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
