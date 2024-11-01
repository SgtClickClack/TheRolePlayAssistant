import logging
import os
import sys
import socket
import time
import signal
from app import create_app
import psutil
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

def kill_processes_on_port(port):
    """Kill processes using the specified port with improved error handling"""
    try:
        logger.info(f"Attempting to kill processes on port {port}")
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections():
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        try:
                            process = psutil.Process(proc.pid)
                            logger.info(f"Found process {proc.pid} using port {port}")
                            process.terminate()
                            process.wait(timeout=3)
                            killed = True
                        except psutil.TimeoutExpired:
                            logger.warning(f"Process {proc.pid} did not terminate gracefully, forcing kill")
                            process.kill()
                            process.wait(timeout=3)
                            killed = True
                        except psutil.NoSuchProcess:
                            logger.warning(f"Process {proc.pid} no longer exists")
                        except Exception as e:
                            logger.error(f"Error killing process {proc.pid}: {str(e)}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"Process error: {str(e)}")
                continue
        
        if killed:
            logger.info("Successfully killed processes on port")
            time.sleep(2)  # Wait for port to be fully released
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
        logger.info(f"Attempting to verify port {port} availability")
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        sock.close()
        logger.info(f"Port {port} is available")
        return True
    except socket.error as e:
        logger.error(f"Port {port} verification failed: {str(e)}")
        try:
            sock.close()
        except:
            pass
        return False

def ensure_port_available(port, max_attempts=3):
    """Ensure port is available with improved cleanup"""
    for attempt in range(max_attempts):
        logger.info(f"Attempting to secure port {port} (attempt {attempt + 1}/{max_attempts})")
        
        # Kill any existing processes
        kill_processes_on_port(port)
        
        # Verify port availability
        if verify_port_availability(port):
            logger.info(f"Successfully secured port {port}")
            return True
            
        time.sleep(2)
    
    logger.error(f"Failed to secure port {port} after {max_attempts} attempts")
    return False

class CustomWSGIRequestHandler(WSGIRequestHandler):
    def log(self, type, message, *args):
        """Enhanced logging for requests"""
        if type == 'info':
            logger.info(f"{self.address_string()} - {message % args}")
        elif type == 'warning':
            logger.warning(f"{self.address_string()} - {message % args}")
        else:
            logger.error(f"{self.address_string()} - {message % args}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # Ensure port is available
        if not ensure_port_available(port):
            logger.error(f"Could not secure port {port}")
            sys.exit(1)
        
        # Create Flask app with debug configuration
        logger.info("Creating Flask application")
        app = create_app()
        
        # Update configuration
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,
            SERVER_NAME=None
        )
        
        # Start server with improved error handling
        logger.info(f"Starting Flask application on {host}:{port}")
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
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
