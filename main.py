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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def kill_processes_on_port(port):
    """Kill processes using the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process = psutil.Process(proc.pid)
                for conn in process.net_connections():
                    if conn.laddr.port == port:
                        process.terminate()
                        try:
                            process.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f"Error killing processes: {str(e)}")

def cleanup_resources():
    """Cleanup resources before shutdown"""
    try:
        port = int(os.environ.get('PORT', 5000))
        kill_processes_on_port(port)
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down")
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
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Initial cleanup
        cleanup_resources()
        time.sleep(1)  # Wait for resources to be freed
        
        # Create Flask app
        app = create_app()
        if not app:
            logger.error("Failed to create Flask application")
            sys.exit(1)

        # Start server
        logger.info(f"Starting Flask server on {host}:{port}")
        run_simple(
            hostname=host,
            port=port,
            application=app,
            use_reloader=False,
            use_debugger=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        cleanup_resources()
        sys.exit(1)
