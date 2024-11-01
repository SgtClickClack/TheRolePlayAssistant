import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import logging
from sqlalchemy import text
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

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

def create_app():
    """Create and configure the Flask application"""
    try:
        # Create Flask app with explicit template and static folders
        app = Flask(__name__, 
                  template_folder='templates',
                  static_folder='static',
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
            SESSION_TYPE="filesystem",
            TEMPLATES_AUTO_RELOAD=True,
            DEBUG=True,
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
            SEND_FILE_MAX_AGE_DEFAULT=0,
            EXPLAIN_TEMPLATE_LOADING=True,
            JSON_AS_ASCII=False,
            USE_RELOADER=False
        )
        
        # Ensure required directories exist
        for directory in ['templates', 'static', 'static/uploads', 'static/css', 'static/js', 'flask_session']:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
        
        # Initialize extensions
        db.init_app(app)
        csrf.init_app(app)
        Session(app)
        
        # Initialize login manager
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        
        # Import models and routes within app context
        with app.app_context():
            from models import User
            from routes import register_routes
            
            # Create database tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Register routes
            register_routes(app)
            logger.info("Routes registered successfully")
            
            # Verify database connection
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection verified")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        raise

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
