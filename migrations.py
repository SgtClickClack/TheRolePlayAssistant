from app import app, db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def add_spiciness_level_column():
    try:
        with app.app_context():
            # Check if column exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name='user' 
                    AND column_name='spiciness_level'
                )
            """))
            column_exists = result.scalar()
            
            if not column_exists:
                logger.info("Adding spiciness_level column to user table")
                # Add the column with a default value
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN spiciness_level INTEGER DEFAULT 1 NOT NULL
                """))
                db.session.commit()
                logger.info("Successfully added spiciness_level column")
                return True
            else:
                logger.info("spiciness_level column already exists")
                return True
    except Exception as e:
        logger.error(f"Error adding spiciness_level column: {str(e)}")
        db.session.rollback()
        return False

def verify_schema():
    try:
        with app.app_context():
            # Verify column exists and has correct properties
            result = db.session.execute(text("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user' AND column_name = 'spiciness_level'
            """))
            column_info = result.fetchone()
            
            if column_info:
                logger.info(f"Column verification successful: {column_info}")
                return True
            logger.error("Column verification failed: column not found")
            return False
    except Exception as e:
        logger.error(f"Error verifying schema: {str(e)}")
        return False

if __name__ == "__main__":
    if add_spiciness_level_column():
        verify_schema()
