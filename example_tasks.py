from app import create_app, db
from models import Scenario, ScavengerHuntTask
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_example_tasks():
    """Create example tasks with proper error handling"""
    app = create_app()
    with app.app_context():
        try:
            # Create an indoor scavenger hunt scenario
            indoor_scenario = Scenario(
                title="Office Adventure Hunt",
                description="Find and photograph these objects in your environment!",
                setting="Office or Home",
                challenge="Complete various photo tasks",
                goal="Complete all photo challenges",
                points=500
            )
            db.session.add(indoor_scenario)
            db.session.flush()

            # Create tasks for the indoor scenario
            indoor_tasks = [
                {
                    "description": "Find a workspace setup with both a computer and a coffee mug",
                    "required_objects": ["laptop", "cup"],
                    "object_confidence": 0.6,
                    "points": 100
                }
            ]

            # Add indoor tasks
            for task_data in indoor_tasks:
                task = ScavengerHuntTask(
                    scenario_id=indoor_scenario.id,
                    **task_data
                )
                db.session.add(task)

            db.session.commit()
            logger.info("Example tasks created successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to create example tasks: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if not create_example_tasks():
        exit(1)
