import logging
import os
import sys
import time
from werkzeug.serving import run_simple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_port(port, host='0.0.0.0', timeout=30):
    """Wait for the port to be available"""
    import socket
    start_time = time.time()
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((host, port))
                return True
        except socket.error:
            if time.time() - start_time >= timeout:
                return False
            time.sleep(1)

if __name__ == "__main__":
    try:
        # Import app after configuring logging
        from app import app
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        # Wait for port to be available
        if not wait_for_port(port):
            logger.error(f"Port {port} is not available after timeout")
            sys.exit(1)
            
        logger.info(f"Starting Flask application on {host}:{port}")
        logger.info(f"Template folder: {app.template_folder}")
        logger.info(f"Static folder: {app.static_folder}")
        
        # Use run_simple for better port binding
        run_simple(
            hostname=host,
            port=port,
            application=app,
            use_reloader=False,
            use_debugger=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
