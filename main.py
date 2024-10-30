from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text
from datetime import datetime, timedelta
import logging
import os
import uuid
import socket
import sys
import signal
import psutil
import time
from app import app, db
from models import Character, Scenario, CharacterTemplate, Achievement, ScenarioCompletion, User, ScavengerHuntTask, TaskSubmission

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def verify_database():
    """Verify database connection"""
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection verified")
            return True
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")
        return False

def verify_directories():
    """Verify required directories exist"""
    try:
        # Verify static directory
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        # Verify template directory
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if not os.path.exists(template_dir):
            logger.error(f"Template directory missing: {template_dir}")
            return False
            
        # Verify uploads directory
        upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        logger.info("All directories verified")
        return True
    except Exception as e:
        logger.error(f"Directory verification failed: {str(e)}")
        return False

def kill_processes_on_port(port):
    """Kill all processes using the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                conns = proc.connections()  # Use net_connections() in future versions
                for conn in conns:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        os.kill(proc.pid, signal.SIGTERM)
                        logger.info(f"Terminated process {proc.pid} using port {port}")
                        time.sleep(1)  # Give process time to release resources
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return True
    except Exception as e:
        logger.error(f"Error killing processes on port {port}: {str(e)}")
        return False

def ensure_port_available(port, max_attempts=3):
    """Ensure the specified port is available"""
    for attempt in range(max_attempts):
        try:
            # Try to kill any processes using the port
            kill_processes_on_port(port)
            
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                s.close()
                logger.info(f"Port {port} is available")
                return True
        except socket.error as e:
            logger.warning(f"Port {port} is in use (attempt {attempt + 1}/{max_attempts}): {str(e)}")
            if attempt == max_attempts - 1:
                logger.error(f"Failed to secure port {port} after {max_attempts} attempts")
                return False
            time.sleep(2)  # Wait before retrying
    return False

# Import routes after app initialization
import routes

if __name__ == "__main__":
    try:
        # Configure Flask app
        app.config['EXPLAIN_TEMPLATE_LOADING'] = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['JSON_SORT_KEYS'] = False
        app.jinja_env.auto_reload = True
        
        # Verify database and directories
        if not verify_database() or not verify_directories():
            logger.error("Failed to verify database or directories")
            sys.exit(1)

        # Ensure port 5000 is available
        if not ensure_port_available(5000):
            logger.error("Could not secure port 5000")
            sys.exit(1)

        # Start Flask application
        logger.info("Starting Flask application on port 5000")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False to avoid duplicate process issues
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
