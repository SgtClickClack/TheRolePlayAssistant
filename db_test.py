from app import create_app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_db_connection():
    """Test database connection with proper error handling"""
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection successful!")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False

if __name__ == "__main__":
    if not test_db_connection():
        exit(1)
