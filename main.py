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
    level=logging.DEBUG,
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
        upload_dir = app.config.get("UPLOAD_FOLDER", "static/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        logger.info("All directories verified")
        return True
    except Exception as e:
        logger.error(f"Directory verification failed: {str(e)}")
        return False

def wait_for_port_release(port, timeout=30):
    """Wait for a port to be released"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                s.close()
                logger.info(f"Port {port} is now available")
                return True
        except socket.error:
            logger.debug(f"Port {port} still in use, waiting...")
            time.sleep(1)
    return False

def kill_process_on_port(port):
    """Find and kill any process using the specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    os.kill(proc.pid, signal.SIGTERM)
                    logger.info(f"Terminated process {proc.pid} using port {port}")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def ensure_port_available(port, max_attempts=3):
    """Ensure the specified port is available"""
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                s.close()
                logger.info(f"Port {port} is available")
                return True
        except socket.error:
            logger.warning(f"Port {port} is in use (attempt {attempt + 1}/{max_attempts})")
            if kill_process_on_port(port):
                if wait_for_port_release(port):
                    continue
            if attempt == max_attempts - 1:
                logger.error(f"Failed to secure port {port} after {max_attempts} attempts")
                return False
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

        # Add delay to ensure port is fully released
        time.sleep(2)

        # Start Flask application
        logger.info("Starting Flask application on port 5000")
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
