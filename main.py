import os
import sys
import time
import signal
import socket
import psutil
import logging
import atexit
from app import create_app
from werkzeug.serving import run_simple

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flask_debug.log')
    ]
)
logger = logging.getLogger(__name__)

def kill_processes_on_port(port):
    """Kill processes using the specified port with improved error handling"""
    try:
        logger.info(f"Attempting to kill processes on port {port}")
        killed = False
        
        # First try to find and kill any Python processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.name().lower():
                    process = psutil.Process(proc.pid)
                    try:
                        # Check if process is using the port
                        for conn in process.connections(kind='inet'):
                            if hasattr(conn, 'laddr') and conn.laddr.port == port:
                                logger.info(f"Found process {proc.pid} using port {port}")
                                process.terminate()
                                try:
                                    process.wait(timeout=1)
                                    killed = True
                                    logger.info(f"Successfully terminated process {proc.pid}")
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
            time.sleep(0.5)  # Reduced wait time
        return True
    except Exception as e:
        logger.error(f"Error killing processes: {str(e)}")
        return False

def verify_port_availability(port, max_attempts=3):
    """Verify if port is available with improved error handling"""
    for attempt in range(max_attempts):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(0.5)
            sock.bind(('0.0.0.0', port))
            sock.listen(1)
            logger.info(f"Port {port} is available")
            return True
        except socket.error as e:
            logger.warning(f"Port {port} verification failed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(0.5)
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass
    
    logger.error(f"Port {port} is not available after {max_attempts} attempts")
    return False

def verify_server_running(port, timeout=15):
    """Verify if server is actually running and responding"""
    logger.info(f"Verifying server on port {port}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                result = sock.connect_ex(('127.0.0.1', port))
                
                if result == 0:
                    # Try HTTP connection
                    sock.send(b"GET / HTTP/1.0\r\n\r\n")
                    response = sock.recv(1024)
                    if response:
                        logger.info(f"Server verified running on port {port}")
                        return True
        except Exception as e:
            logger.debug(f"Server verification attempt failed: {str(e)}")
        
        time.sleep(0.2)
    
    logger.error("Server verification timed out")
    return False

def cleanup_resources():
    """Cleanup resources before shutdown"""
    logger.info("Cleaning up resources...")
    try:
        port = int(os.environ.get('PORT', 5000))
        kill_processes_on_port(port)
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully")
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
        
        # Verify port availability
        if not verify_port_availability(port):
            logger.error("Could not secure required port")
            sys.exit(1)
            
        # Create Flask app
        app = create_app()
        if not app:
            logger.error("Failed to create Flask application")
            sys.exit(1)
        
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
                use_evalex=False  # Disable werkzeug debugger
            )
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            sys.exit(1)
            
        # Verify server is running
        if not verify_server_running(port):
            logger.error("Server failed to start properly")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        cleanup_resources()
        sys.exit(1)
