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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create Flask app with explicit template and static folders
    app = Flask(__name__,
                static_folder=os.path.join(current_dir, 'static'),
                static_url_path='/static',
                template_folder=os.path.join(current_dir, 'templates'))
    
    # Configure app
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(current_dir, 'static', 'uploads')
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["DEBUG"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching for development
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["PREFERRED_URL_SCHEME"] = "http"  # Add this for proper URL generation

    # Template configuration
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}  # Disable template caching in development
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Initialize extensions
    Session(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize directories with proper error handling
    try:
        # Create required directories
        required_dirs = [
            'static', 'templates',
            os.path.join('static', 'css'),
            os.path.join('static', 'js'),
            os.path.join('static', 'uploads')
        ]
        
        for dir_path in required_dirs:
            abs_path = os.path.join(current_dir, dir_path)
            if not os.path.exists(abs_path):
                os.makedirs(abs_path, exist_ok=True)
                logger.info(f"Created directory: {abs_path}")

            # Verify directory permissions
            if not os.access(abs_path, os.W_OK):
                logger.error(f"Directory not writable: {abs_path}")
                raise RuntimeError(f"Directory not writable: {abs_path}")
                
            logger.info(f"Verified directory: {abs_path}")

        # Create default static files if they don't exist
        static_files = {
            os.path.join(app.static_folder, 'css', 'custom.css'): '/* Custom styles for dark theme */',
            os.path.join(app.static_folder, 'js', 'main.js'): '// Main JavaScript file'
        }

        for file_path, content in static_files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Created default file: {file_path}")

    except Exception as e:
        logger.error(f"Failed to initialize directories: {str(e)}")
        raise

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

    return app

# Create the Flask application
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
