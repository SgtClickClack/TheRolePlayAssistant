from flask import Flask
import logging
import os
import sys
import socket
import signal
import psutil
import time
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_socket(port):
    """Cleanup function to release the socket on exit"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        sock.close()
        logger.info(f"Released port {port}")
    except Exception as e:
        logger.error(f"Error releasing port {port}: {str(e)}")

def kill_processes_on_port(port):
    """Kill all processes using the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == port:
                        os.kill(proc.pid, signal.SIGTERM)
                        logger.info(f"Terminated process {proc.pid} using port {port}")
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f"Error killing processes on port {port}: {str(e)}")

if __name__ == "__main__":
    port = 5000
    
    try:
        # Import app after socket cleanup
        from app import app
        
        # Register cleanup function
        atexit.register(cleanup_socket, port)
        
        # Kill any existing processes using the port
        kill_processes_on_port(port)
        
        # Add small delay to ensure port is released
        time.sleep(2)
        
        # Start Flask application
        logger.info(f"Starting Flask application on port {port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=False,  # Disable reloader to prevent duplicate processes
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
