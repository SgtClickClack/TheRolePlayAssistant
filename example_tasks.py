from app import app, db
from models import Scenario, ScavengerHuntTask

def create_example_tasks():
    with app.app_context():
        # Create a scavenger hunt scenario
        scenario = Scenario(
            title="Office Adventure Hunt",
            description="Find and photograph these everyday objects in your environment!",
            setting="Office or Home",
            challenge="Photograph common objects",
            goal="Complete all photo tasks",
            points=300
        )
        db.session.add(scenario)
        db.session.flush()

        # Create tasks for the scenario
        tasks = [
            {
                "description": "Find and photograph a coffee cup or mug",
                "required_object": "cup",
                "object_confidence": 0.6,
                "points": 50
            },
            {
                "description": "Take a photo of any book",
                "required_object": "book",
                "object_confidence": 0.6,
                "points": 50
            },
            {
                "description": "Find and photograph a laptop or computer",
                "required_object": "laptop",
                "object_confidence": 0.6,
                "points": 50
            }
        ]

        for task_data in tasks:
            task = ScavengerHuntTask(
                scenario_id=scenario.id,
                **task_data
            )
            db.session.add(task)

        db.session.commit()

if __name__ == "__main__":
    create_example_tasks()
