import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    # Get the absolute path of the current directory
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Create Flask app with explicit template and static folders
    app = Flask(__name__, 
                template_folder=os.path.join(current_dir, 'templates'),
                static_folder=os.path.join(current_dir, 'static'),
                static_url_path='/static')
    
    # Configure app
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        },
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(current_dir, 'static', 'uploads'),
        SESSION_TYPE="filesystem",
        TEMPLATES_AUTO_RELOAD=True,
        DEBUG=True,
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
        SEND_FILE_MAX_AGE_DEFAULT=0,  # Disable caching for development
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        APPLICATION_ROOT='/'  # Ensure root path is set
    )

    # Initialize directories
    try:
        for dir_path in ['static', 'templates', 'static/css', 'static/js', 'static/uploads']:
            abs_path = os.path.join(current_dir, dir_path)
            os.makedirs(abs_path, exist_ok=True)
            if not os.access(abs_path, os.W_OK):
                raise RuntimeError(f"Directory not writable: {abs_path}")
            logger.info(f"Verified directory: {abs_path}")

    except Exception as e:
        logger.error(f"Failed to initialize directories: {str(e)}")
        raise

    # Initialize extensions
    Session(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Import and register routes after app initialization
    with app.app_context():
        # Import models first
        from models import User
        logger.info("Models imported successfully")
        
        # Import and register routes
        from routes import register_routes
        app = register_routes(app)
        logger.info("Routes registered successfully")
        
        # Verify database connection
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection verified")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

        # Log template and static folder locations
        logger.info(f"Template folder: {app.template_folder}")
        logger.info(f"Static folder: {app.static_folder}")
        logger.info(f"Static URL path: {app.static_url_path}")
        
        # Verify template directory exists and is readable
        if not os.path.exists(app.template_folder):
            raise RuntimeError(f"Template folder not found: {app.template_folder}")
        if not os.access(app.template_folder, os.R_OK):
            raise RuntimeError(f"Template folder not readable: {app.template_folder}")

    return app

# Create the Flask application
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
