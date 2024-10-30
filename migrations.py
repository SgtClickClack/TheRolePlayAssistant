from app import app, db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def add_scavenger_hunt_tables():
    try:
        with app.app_context():
            # Create ScavengerHuntTask table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS scavenger_hunt_task (
                    id SERIAL PRIMARY KEY,
                    scenario_id INTEGER REFERENCES scenario(id),
                    description TEXT NOT NULL,
                    required_object VARCHAR(100) NOT NULL,
                    object_confidence FLOAT DEFAULT 0.7,
                    points INTEGER DEFAULT 50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create TaskSubmission table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS task_submission (
                    id SERIAL PRIMARY KEY,
                    task_id INTEGER REFERENCES scavenger_hunt_task(id),
                    user_id INTEGER REFERENCES "user"(id),
                    photo_path VARCHAR(255) NOT NULL,
                    confidence_score FLOAT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP
                )
            """))
            
            db.session.commit()
            logger.info("Successfully created scavenger hunt tables")
            return True
    except Exception as e:
        logger.error(f"Error creating scavenger hunt tables: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    add_scavenger_hunt_tables()
