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

def verify_server_running(port, max_attempts=60, timeout=0.5):
    """Verify if server is actually running and responding"""
    logger.info(f"Verifying server on port {port}")
    start_time = time.time()
    
    for attempt in range(max_attempts):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                logger.info(f"Server verified running on port {port}")
                return True
        except Exception as e:
            logger.debug(f"Server verification attempt {attempt + 1} failed: {str(e)}")
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
        
        # More frequent checks with shorter intervals
        time.sleep(0.2)
        
        # Check for overall timeout
        if time.time() - start_time > 30:  # 30 seconds total timeout
            logger.error("Server verification timed out")
            return False
    
    logger.error("Server verification failed")
    return False

def kill_processes_on_port(port):
    """Kill processes using the specified port"""
    try:
        killed = False
        logger.info(f"Scanning for processes using port {port}")
        
        # First try to find any existing Python/Flask processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process = psutil.Process(proc.pid)
                try:
                    connections = process.connections('inet')
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr.port == port:
                            logger.info(f"Found process {proc.pid} using port {port}")
                            try:
                                process.terminate()
                                process.wait(timeout=2)
                                killed = True
                            except psutil.TimeoutExpired:
                                logger.warning(f"Process {proc.pid} did not terminate gracefully, forcing kill")
                                process.kill()
                                process.wait(timeout=1)
                                killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if killed:
            logger.info("Waiting for port to be fully released")
            time.sleep(1)
        return killed
    except Exception as e:
        logger.error(f"Error killing processes: {str(e)}")
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
        logger.info(f"Port {port} is available")
        return True
    except socket.error as e:
        logger.error(f"Port verification failed: {str(e)}")
        return False
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass

def ensure_port_available(port, max_attempts=5):
    """Ensure port is available"""
    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1}/{max_attempts} to secure port {port}")
        
        # Kill any existing processes
        kill_processes_on_port(port)
        
        # Verify port availability
        if verify_port_availability(port):
            logger.info(f"Successfully secured port {port}")
            return True
        
        if attempt < max_attempts - 1:
            logger.info("Waiting before retry")
            time.sleep(1)
    
    logger.error(f"Failed to secure port {port}")
    return False

class CustomWSGIRequestHandler(WSGIRequestHandler):
    """Enhanced request handler"""
    protocol_version = "HTTP/1.1"
    
    def handle(self):
        try:
            super().handle()
        except Exception as e:
            logger.error(f"Request handling error: {str(e)}")

def cleanup_resources():
    """Cleanup resources before shutdown"""
    try:
        logger.info("Cleaning up resources...")
        port = int(os.environ.get('PORT', 5000))
        kill_processes_on_port(port)
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
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server initialization on {host}:{port}")
        
        # Initial cleanup
        cleanup_resources()
        time.sleep(1)
        
        # Ensure port is available
        if not ensure_port_available(port):
            logger.error("Could not secure required port. Exiting.")
            sys.exit(1)
        
        # Create and configure app
        app = create_app()
        app.config.update(
            DEBUG=True,
            TEMPLATES_AUTO_RELOAD=True,
            USE_RELOADER=False,
            SERVER_NAME=None,
            APPLICATION_ROOT='/',
            ENV='development'
        )
        
        # Start server
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
        
    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        sys.exit(1)
