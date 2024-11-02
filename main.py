import os
import sys
import time
import signal
import socket
import logging
import atexit
from app import create_app, db
from werkzeug.serving import WSGIRequestHandler, run_simple
from sqlalchemy import text

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomWSGIRequestHandler(WSGIRequestHandler):
    """Enhanced request handler with better logging"""
    protocol_version = "HTTP/1.1"
    
    def log(self, type, message, *args):
        """Enhanced logging for requests"""
        if type == 'info':
            logger.info(f"{self.address_string()} - {message % args}")
        elif type == 'warning':
            logger.warning(f"{self.address_string()} - {message % args}")
        else:
            logger.error(f"{self.address_string()} - {message % args}")

def verify_port_availability(port, retries=5):
    """Verify if port is available with improved retry mechanism"""
    for attempt in range(retries):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1)
            sock.bind(('0.0.0.0', port))
            sock.listen(1)
            logger.info(f"Port {port} is available (attempt {attempt + 1})")
            sock.close()
            return True
        except socket.error as e:
            logger.warning(f"Port {port} verification attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(1)
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

    logger.error(f"Port {port} verification failed after {retries} attempts")
    return False

def verify_server_running(port, max_attempts=30):
    """Verify if server is actually running and responding"""
    logger.info(f"Verifying server on port {port}")
    start_time = time.time()

    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                logger.info(f"Server verified running on port {port}")
                return True
        except Exception as e:
            logger.debug(f"Server verification attempt {attempt + 1} failed: {str(e)}")

        time.sleep(0.2)
        if time.time() - start_time > 15:  # 15 seconds total timeout
            logger.error("Server verification timed out")
            return False

    logger.error("Server verification failed")
    return False

def verify_database_connection(app, retries=5):
    """Verify database connection with retries"""
    for attempt in range(retries):
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                logger.info("Database connection verified successfully")
                return True
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(1)

    logger.error(f"Database connection failed after {retries} attempts")
    return False

def cleanup_resources():
    """Cleanup resources before shutdown"""
    logger.info("Cleaning up resources...")
    try:
        # Close database connections
        try:
            db.session.remove()
            db.engine.dispose()
        except:
            pass

        # Flush output buffers
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown")
    cleanup_resources()
    sys.exit(0)

def run_flask_app():
    """Run Flask application with robust initialization and error handling"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        atexit.register(cleanup_resources)

        # Use port 5000 for development
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Required for Replit webview
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # Initial cleanup
        cleanup_resources()

        # Verify port availability
        if not verify_port_availability(port, retries=5):
            logger.error(f"Port {port} is not available")
            return False

        # Create Flask app
        logger.info("Creating Flask application")
        app = create_app()
        if not app:
            logger.error("Failed to create Flask application")
            return False

        # Verify database connection
        if not verify_database_connection(app, retries=5):
            logger.error("Failed to verify database connection")
            return False

        # Configure for Replit environment
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,
            SERVER_NAME=None,
            APPLICATION_ROOT='/',
            JSON_AS_ASCII=False,
            EXPLAIN_TEMPLATE_LOADING=True,
            MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
            SEND_FILE_MAX_AGE_DEFAULT=0
        )

        # Start server with improved configuration
        logger.info(f"Starting Flask application on {host}:{port}")
        try:
            run_simple(
                hostname=host,
                port=port,
                application=app,
                use_reloader=False,
                use_debugger=True,
                threaded=True,
                request_handler=CustomWSGIRequestHandler,
                static_files={'/static': 'static'}  # Enable static file serving
            )

            # Verify server is running
            if not verify_server_running(port):
                logger.error("Server failed to start properly")
                return False

            return True
        except Exception as e:
            logger.error(f"Server failed to start: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    if not run_flask_app():
        sys.exit(1)
