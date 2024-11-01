import logging
import os
import sys
import socket
import time
import signal
from app import create_app
import psutil
from werkzeug.serving import WSGIRequestHandler

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def kill_processes_on_port(port):
    """Kill processes using the specified port with improved error handling"""
    try:
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        logger.info(f"Found process {proc.pid} using port {port}")
                        psutil.Process(proc.pid).terminate()
                        killed = True
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                logger.warning(f"Process error: {str(e)}")
                continue
        if killed:
            time.sleep(2)  # Wait longer after killing processes
        return True
    except Exception as e:
        logger.error(f"Error killing processes on port {port}: {str(e)}")
        return False

def verify_port_availability(port):
    """Verify if port is available with improved error handling"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1)
    
    try:
        # First try to connect to check if port is in use
        result = sock.connect_ex(('0.0.0.0', port))
        if result == 0:
            logger.warning(f"Port {port} is already in use")
            sock.close()
            return False
            
        # If connection failed (port not in use), try to bind
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        sock.close()
        logger.info(f"Successfully verified port {port} availability")
        return True
    except Exception as e:
        logger.error(f"Error verifying port {port}: {str(e)}")
        try:
            sock.close()
        except:
            pass
        return False

def ensure_port_available(port, max_attempts=5):
    """Ensure port is available with improved retry mechanism"""
    for attempt in range(max_attempts):
        logger.info(f"Checking port {port} availability (attempt {attempt + 1}/{max_attempts})")
        
        if verify_port_availability(port):
            logger.info(f"Port {port} is available")
            time.sleep(1)  # Add small delay after verification
            return True
            
        if kill_processes_on_port(port):
            logger.info(f"Cleared processes using port {port}")
            time.sleep(2)  # Wait for port to fully clear
            if verify_port_availability(port):
                time.sleep(1)  # Add small delay after verification
                return True
                
        logger.warning(f"Port {port} still in use, retrying...")
        time.sleep(2)
    
    logger.error(f"Failed to secure port {port} after {max_attempts} attempts")
    return False

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal. Cleaning up...")
    try:
        port = int(os.environ.get('PORT', 5000))
        kill_processes_on_port(port)
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
    sys.exit(0)

class CustomRequestHandler(WSGIRequestHandler):
    """Custom request handler with improved logging"""
    def log(self, type, message, *args):
        """Override to add request details to logs"""
        if type == 'info':
            logger.info(f"{self.address_string()} - {message % args}")
        elif type == 'warning':
            logger.warning(f"{self.address_string()} - {message % args}")
        else:
            logger.error(f"{self.address_string()} - {message % args}")

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        host = '0.0.0.0'
        port = int(os.environ.get('PORT', 5000))
        
        # Ensure port is available
        if not ensure_port_available(port):
            raise RuntimeError(f"Unable to secure port {port}")
            
        # Create and configure app
        app = create_app()
        
        # Configure server settings
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,
            SERVER_NAME=None,
            APPLICATION_ROOT='/',
            PREFERRED_URL_SCHEME='http'
        )
        
        logger.info(f"Starting Flask application on {host}:{port}")
        
        # Run the application with the custom request handler
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=False,
            threaded=True,
            request_handler=CustomRequestHandler
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
