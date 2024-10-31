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
    level=logging.INFO,
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
    # Get absolute paths for template and static directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    # Create Flask app with explicit template and static folders
    app = Flask(__name__)
    app.template_folder = template_dir
    app.static_folder = static_dir
    app.static_url_path = '/static'
    
    # Configure app
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
        EXPLAIN_TEMPLATE_LOADING=True  # Enable template loading debugging
    )
    
    # Create required directories if they don't exist
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
    Session(app)
    csrf.init_app(app)
    db.init_app(app)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.session_protection = "strong"
    
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Import models and routes
            from models import User  # Required for login manager
            from routes import register_routes
            app = register_routes(app)
            logger.info("Routes registered successfully")
            
            # Verify database connection
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection verified")
            
            # Log configuration
            logger.info(f"Template folder: {app.template_folder}")
            logger.info(f"Static folder: {app.static_folder}")
            logger.info(f"Static URL path: {app.static_url_path}")
            
        except Exception as e:
            logger.error(f"Application initialization failed: {str(e)}")
            raise
    
    return app

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
