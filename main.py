import os
import sys
import time
import signal
import socket
import logging
import atexit
from app import create_app
from werkzeug.serving import WSGIRequestHandler, run_simple

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

def cleanup_resources():
    """Cleanup resources before shutdown"""
    try:
        logger.info("Cleaning up resources...")
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown")
    cleanup_resources()
    sys.exit(0)

def run_flask_app():
    """Run Flask application with proper Replit configuration"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        atexit.register(cleanup_resources)

        # Get host and port from environment or use defaults
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Required for Replit webview
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # Initial cleanup
        cleanup_resources()

        # Create and configure app
        app = create_app()
        if not app:
            logger.error("Failed to create Flask application")
            return False

        # Update configuration for Replit webview
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,  # Disable reloader for Replit
            SERVER_NAME=None,  # Allow all hostnames
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
                static_files={'/static': 'static'}
            )
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
