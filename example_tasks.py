from app import app, db
from models import Scenario, ScavengerHuntTask
from datetime import datetime, timedelta

def create_example_tasks():
    with app.app_context():
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

        # Create an outdoor scenario
        outdoor_scenario = Scenario(
            title="City Explorer Challenge",
            description="Explore your city and capture these moments!",
            setting="City/Outdoors",
            challenge="Visit locations and complete photo tasks",
            goal="Document your city adventure",
            points=1000
        )
        db.session.add(outdoor_scenario)
        db.session.flush()

        # Create tasks for the indoor scenario
        indoor_tasks = [
            {
                "description": "Find a workspace setup with both a computer and a coffee mug",
                "required_objects": ["laptop", "cup"],
                "object_confidence": 0.6,
                "points": 100
            },
            {
                "description": "Take a photo of yourself in a 'thinking pose' next to a bookshelf",
                "required_objects": ["book"],
                "required_pose": "thinking",
                "object_confidence": 0.6,
                "points": 150
            },
            {
                "description": "Strike a 'T-pose' in front of your workspace",
                "required_objects": ["chair", "desk"],
                "required_pose": "t_pose",
                "object_confidence": 0.6,
                "points": 200
            }
        ]

        # Create time-sensitive outdoor tasks
        now = datetime.utcnow()
        outdoor_tasks = [
            {
                "description": "Visit and photograph a local landmark with your hands raised",
                "required_objects": ["building", "monument"],
                "required_pose": "hands_up",
                "required_location": "landmark",
                "object_confidence": 0.6,
                "points": 300,
                "start_time": now,
                "end_time": now + timedelta(hours=24)
            },
            {
                "description": "Find and photograph a busy street corner with both a traffic light and a street sign",
                "required_objects": ["traffic light", "sign"],
                "required_location": "street",
                "object_confidence": 0.6,
                "points": 250,
                "time_limit": 30  # 30 minutes to complete
            },
            {
                "description": "Take a photo of yourself doing a victory pose in a park",
                "required_objects": ["tree", "bench"],
                "required_pose": "victory",
                "required_location": "park",
                "object_confidence": 0.6,
                "points": 400,
                "start_time": now,
                "end_time": now + timedelta(hours=48)
            }
        ]

        # Add indoor tasks
        for task_data in indoor_tasks:
            task = ScavengerHuntTask(
                scenario_id=indoor_scenario.id,
                **task_data
            )
            db.session.add(task)

        # Add outdoor tasks
        for task_data in outdoor_tasks:
            task = ScavengerHuntTask(
                scenario_id=outdoor_scenario.id,
                **task_data
            )
            db.session.add(task)

        db.session.commit()

if __name__ == "__main__":
    create_example_tasks()
