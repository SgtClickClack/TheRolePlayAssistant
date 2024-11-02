import os
import logging
import time
import uuid
from flask import Flask, render_template, session, request
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from sqlalchemy import text
from models import db

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def verify_database_connection(app, max_retries=5, retry_delay=2):
    """Verify database connection with retries and improved error handling"""
    logger.info("Starting database connection verification")
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Test database connection with timeout
                result = db.session.execute(text('SELECT 1')).fetchone()
                if result is None:
                    raise Exception("Database query returned no result")
                db.session.commit()
                logger.info("Database connection verified successfully")
                return True
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            logger.error("All database connection attempts failed")
            return False

def verify_session_directory():
    """Verify session directory exists and is writable"""
    try:
        session_dir = 'flask_session'
        os.makedirs(session_dir, exist_ok=True)
        test_file = os.path.join(session_dir, '.test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        logger.error(f"Session directory verification failed: {str(e)}")
        return False

def initialize_extensions(app):
    """Initialize Flask extensions with improved error handling"""
    try:
        db.init_app(app)
        Session(app)
        csrf.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        login_manager.login_message_category = 'info'
        logger.info("Extensions initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        return False

def create_app():
    """Create and configure the Flask application with improved error handling"""
    try:
        # Generate unique instance ID for tracking
        instance_id = str(uuid.uuid4())
        logger.info(f"Creating Flask application instance {instance_id}")

        app = Flask(__name__)

        # Configure database URL
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return None

        # Configure app with enhanced security and performance settings
        app.config.update(
            SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(32)),
            SQLALCHEMY_DATABASE_URI=database_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20,
                'pool_size': 5,
                'max_overflow': 10
            },
            SESSION_TYPE="filesystem",
            SESSION_FILE_DIR='flask_session',
            SESSION_PERMANENT=False,
            PERMANENT_SESSION_LIFETIME=1800,
            TEMPLATES_AUTO_RELOAD=True,
            DEBUG=True,
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_SECRET_KEY=os.urandom(32),
            JSON_AS_ASCII=False,
            MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
        )

        # Verify session directory
        if not verify_session_directory():
            logger.error("Failed to verify session directory")
            return None

        # Initialize extensions
        if not initialize_extensions(app):
            return None

        # Verify database connection before proceeding
        if not verify_database_connection(app):
            logger.error("Failed to verify database connection")
            return None

        # Create database tables within context
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Failed to create database tables: {str(e)}")
                return None

            # Import and register routes
            try:
                from routes import register_routes
                register_routes(app)
                logger.info("Routes registered successfully")
            except Exception as e:
                logger.error(f"Failed to register routes: {str(e)}")
                return None

        # Enhanced request logging
        @app.before_request
        def log_request():
            request_id = str(uuid.uuid4())
            session['request_id'] = request_id
            logger.info(f"Request {request_id}: {request.method} {request.url}")

        @app.after_request
        def log_response(response):
            request_id = session.get('request_id', 'unknown')
            logger.info(f"Response for {request_id}: {response.status}")
            return response

        # Enhanced error handlers with detailed logging
        @app.errorhandler(404)
        def not_found_error(error):
            logger.warning(f"404 error for path: {request.path}")
            return render_template('404.html', error_path=request.path), 404

        @app.errorhandler(500)
        def internal_error(error):
            error_id = str(uuid.uuid4())
            logger.error(f"500 error (ID: {error_id}): {str(error)}")
            db.session.rollback()
            return render_template('500.html', error_id=error_id), 500

        @app.errorhandler(Exception)
        def handle_exception(error):
            error_id = str(uuid.uuid4())
            logger.error(f"Unhandled exception (ID: {error_id}): {str(error)}")
            db.session.rollback()
            return render_template('500.html', error_id=error_id), 500

        # Health check endpoint
        @app.route('/health')
        def health_check():
            try:
                result = db.session.execute(text('SELECT 1')).fetchone()
                if result is None:
                    raise Exception("Database query returned no result")
                db.session.commit()
                
                if not verify_session_directory():
                    raise Exception("Session directory not writable")
                
                return {'status': 'healthy', 'instance': instance_id}, 200
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                return {'status': 'unhealthy', 'error': str(e)}, 500

        logger.info(f"Application instance {instance_id} created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        return None

# User loader callback with enhanced error handling
@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        user = User.query.get(int(user_id))
        if user is None:
            logger.warning(f"No user found with ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {str(e)}")
        return None
