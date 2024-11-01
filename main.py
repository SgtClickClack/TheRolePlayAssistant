import os
import sys
import time
import signal
import socket
import psutil
import logging
import atexit
from app import create_app
from werkzeug.serving import WSGIRequestHandler, run_simple

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flask_debug.log')
    ]
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

def verify_port_available(port):
    """Verify if port is available"""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        logger.info(f"Port {port} is available")
        return True
    except socket.error as e:
        logger.error(f"Port {port} is not available: {str(e)}")
        return False
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass

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

if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        atexit.register(cleanup_resources)

        # Get host and port
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # Initial cleanup and port check
        cleanup_resources()

        # Create and configure app
        app = create_app()
        
        # Start server
        if app:
            logger.info(f"Starting Flask application on {host}:{port}")
            try:
                run_simple(
                    hostname=host,
                    port=port,
                    application=app,
                    use_reloader=False,
                    use_debugger=True,
                    threaded=True,
                    request_handler=CustomWSGIRequestHandler
                )
            except Exception as e:
                logger.error(f"Server failed to start: {str(e)}")
                sys.exit(1)
        else:
            logger.error("Failed to create Flask application")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        sys.exit(1)
