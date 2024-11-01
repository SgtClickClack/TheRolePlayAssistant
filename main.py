import logging
import os
import sys
import socket
import time
import signal
import atexit
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

def verify_server_running(port, max_attempts=30, timeout=1):
    """Verify if server is actually running and responding"""
    start_time = time.time()
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex(('127.0.0.1', port)) == 0:
                    logger.info(f"Server verified running on port {port}")
                    return True
        except Exception as e:
            logger.debug(f"Server verification attempt {attempt + 1} failed: {str(e)}")
        
        if time.time() - start_time > timeout * max_attempts:
            logger.error("Server verification timed out")
            return False
            
        time.sleep(0.5)
    return False

def kill_processes_on_port(port):
    """Kill processes using the specified port"""
    try:
        logger.info(f"Attempting to kill processes on port {port}")
        killed = False
        
        # Find and kill any process using the port
        for proc in psutil.process_iter(['pid']):
            try:
                process = psutil.Process(proc.pid)
                for conn in process.connections('inet'):
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        logger.info(f"Found process using port {port}: {proc.pid}")
                        try:
                            process.terminate()
                            process.wait(timeout=3)
                            killed = True
                        except psutil.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=1)
                            killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed:
            logger.info("Successfully terminated processes")
            time.sleep(1)
        return killed
    except Exception as e:
        logger.error(f"Error killing processes on port {port}: {str(e)}")
        return False

def verify_port_availability(port):
    """Verify if port is available"""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        logger.info(f"Successfully verified port {port} availability")
        return True
    except socket.error as e:
        logger.error(f"Port {port} verification failed: {str(e)}")
        return False
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass

def ensure_port_available(port, max_attempts=3):
    """Ensure port is available"""
    for attempt in range(max_attempts):
        logger.info(f"Attempting to secure port {port} (attempt {attempt + 1}/{max_attempts})")
        
        # Kill any existing processes
        kill_processes_on_port(port)
        
        # Verify port availability
        if verify_port_availability(port):
            logger.info(f"Successfully secured port {port}")
            return True
            
        if attempt < max_attempts - 1:
            time.sleep(1)
            
    logger.error(f"Failed to secure port {port} after {max_attempts} attempts")
    return False

class CustomWSGIRequestHandler(WSGIRequestHandler):
    """Enhanced request handler"""
    protocol_version = "HTTP/1.1"
    
    def handle(self):
        """Override handle method to add error handling"""
        try:
            super().handle()
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            
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
    logger.info("Cleaning up resources...")
    try:
        # Kill any remaining processes on the port
        port = int(os.environ.get('PORT', 5000))
        kill_processes_on_port(port)
        
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

if __name__ == "__main__":
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        atexit.register(cleanup_resources)
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # First ensure no other processes are using the port
        if not ensure_port_available(port):
            logger.error("Could not secure required port. Exiting.")
            sys.exit(1)
        
        # Create Flask app
        logger.info("Creating Flask application")
        app = create_app()
        
        # Update configuration for development
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,
            SERVER_NAME=None,
            APPLICATION_ROOT='/',
            ENV='development'
        )
        
        # Start server with improved error handling
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
            
            # Verify server is actually running
            if not verify_server_running(port):
                logger.error("Server failed to start properly")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        sys.exit(1)
