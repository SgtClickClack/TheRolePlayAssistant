from app import app, db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def add_scavenger_hunt_tables():
    try:
        with app.app_context():
            # Drop existing tables if they exist
            db.session.execute(text("""
                DROP TABLE IF EXISTS task_submission;
                DROP TABLE IF EXISTS scavenger_hunt_task;
            """))
            
            # Create ScavengerHuntTask table with new columns
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS scavenger_hunt_task (
                    id SERIAL PRIMARY KEY,
                    scenario_id INTEGER REFERENCES scenario(id),
                    description TEXT NOT NULL,
                    required_objects JSONB NOT NULL,
                    required_pose VARCHAR(100),
                    required_location VARCHAR(200),
                    object_confidence FLOAT DEFAULT 0.7,
                    points INTEGER DEFAULT 50,
                    time_limit INTEGER,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create TaskSubmission table with new columns
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS task_submission (
                    id SERIAL PRIMARY KEY,
                    task_id INTEGER REFERENCES scavenger_hunt_task(id),
                    user_id INTEGER REFERENCES "user"(id),
                    photo_path VARCHAR(255) NOT NULL,
                    confidence_score FLOAT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP,
                    location_data JSONB,
                    pose_data JSONB
                )
            """))
            
            db.session.commit()
            logger.info("Successfully created enhanced scavenger hunt tables")
            return True
    except Exception as e:
        logger.error(f"Error creating scavenger hunt tables: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    add_scavenger_hunt_tables()
