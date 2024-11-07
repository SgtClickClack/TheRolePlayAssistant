import os
import logging
import uuid
from flask import Flask, render_template, session, request
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from sqlalchemy import text
from models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def verify_database_connection(app):
    """Verify database connection"""
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def initialize_extensions(app):
    """Initialize Flask extensions"""
    try:
        db.init_app(app)
        Session(app)
        csrf.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        return True
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        return False

def create_app():
    """Create and configure the Flask application"""
    try:
        app = Flask(__name__)
        
        # Configure app
        app.config.update(
            SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', os.urandom(32)),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SESSION_TYPE='filesystem',
            SESSION_FILE_DIR='flask_session',
            TEMPLATES_AUTO_RELOAD=True
        )
        
        # Initialize extensions
        if not initialize_extensions(app):
            return None
            
        # Verify database connection
        if not verify_database_connection(app):
            return None
            
        # Create database tables
        with app.app_context():
            db.create_all()
            
        # Import and register routes
        from routes import register_routes
        register_routes(app)
        
        # Request logging
        @app.before_request
        def log_request():
            request_id = str(uuid.uuid4())
            session['request_id'] = request_id
            logger.info(f"Request {request_id}: {request.method} {request.path}")
        
        @app.after_request
        def log_response(response):
            request_id = session.get('request_id', 'unknown')
            logger.info(f"Response {request_id}: {response.status}")
            return response
        
        # Error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html'), 404
            
        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template('500.html'), 500
            
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        return None

@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {str(e)}")
        return None
