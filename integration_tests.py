import os
import unittest
import logging
import json
from sqlalchemy import text
from app import create_app
from models import db, User, Character, CharacterTemplate, Scenario, Achievement, TaskSubmission
from story_generator import generate_story_scene
from werkzeug.datastructures import FileStorage
from io import BytesIO
from flask_session import Session
from cachelib.file import FileSystemCache
import shutil

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        logger.info("Setting up test environment...")
        try:
            # Clean up any existing session files
            session_dir = os.path.join(os.getcwd(), 'flask_session')
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
            os.makedirs(session_dir, exist_ok=True)

            # Create the Flask application
            cls.app = create_app()
            if not cls.app:
                raise RuntimeError("Failed to create Flask application")
            
            # Configure for testing
            cls.app.config.update({
                'TESTING': True,
                'WTF_CSRF_ENABLED': False,
                'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
                'SECRET_KEY': 'test_secret_key',
                'SESSION_TYPE': 'filesystem',
                'SESSION_FILE_DIR': session_dir,
                'SESSION_PERMANENT': False,
                'PERMANENT_SESSION_LIFETIME': 1800
            })
            
            # Create application context
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            # Initialize session
            Session(cls.app)
            
            # Create database tables
            db.create_all()
            logger.info("Test environment setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            raise

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        logger.info("Cleaning up test environment...")
        try:
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()
            
            # Clean up session files
            session_dir = os.path.join(os.getcwd(), 'flask_session')
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
            logger.info("Test environment cleanup completed")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            raise

    def setUp(self):
        """Set up before each test"""
        self.client = self.app.test_client()
        self.cleanup_database()
        logger.info(f"Starting test: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test"""
        logger.info(f"Finished test: {self._testMethodName}")
        db.session.rollback()

    def cleanup_database(self):
        """Clean up database tables with improved error handling"""
        try:
            db.session.rollback()
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
            logger.info("Database cleaned up successfully")
        except Exception as e:
            logger.error(f"Database cleanup failed: {str(e)}")
            db.session.rollback()
            raise

    # 1. Database Connection Tests
    def test_database_connection(self):
        """Test database connectivity and schema"""
        logger.info("Testing database connection and schema...")
        try:
            # Test basic connection
            result = db.session.execute(text('SELECT 1')).scalar()
            self.assertEqual(result, 1)
            
            # Verify tables exist
            tables = ['user', 'character', 'character_template', 'scenario', 
                     'achievement', 'scenario_completion', 'scavenger_hunt_task', 
                     'task_submission']
            for table in tables:
                result = db.session.execute(
                    text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table}')")
                ).scalar()
                self.assertTrue(result, f"Table {table} does not exist")
            
            logger.info("Database connection and schema test passed")
        except Exception as e:
            logger.error(f"Database test failed: {str(e)}")
            raise

    # 2. User Authentication Tests
    def test_user_authentication_flow(self):
        """Test complete user authentication flow"""
        logger.info("Testing user authentication flow...")
        try:
            # Test registration
            register_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpassword'
            }
            response = self.client.post('/register', data=register_data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Verify user creation
            user = User.query.filter_by(email=register_data['email']).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, register_data['username'])
            
            # Test login
            response = self.client.post('/login', data={
                'email': register_data['email'],
                'password': register_data['password']
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Test session
            with self.client.session_transaction() as session:
                self.assertIn('_fresh', session)
                self.assertTrue(session['_fresh'])
            
            # Test logout
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # Verify session cleared after logout
            with self.client.session_transaction() as session:
                self.assertNotIn('_fresh', session)
            
            logger.info("User authentication flow test passed")
        except Exception as e:
            logger.error(f"Authentication test failed: {str(e)}")
            raise

    # 3. Character System Tests
    def test_character_system(self):
        """Test character creation, templates, and viewing"""
        logger.info("Testing character system...")
        try:
            # Create test user and login
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

            with self.client as c:
                # Login
                c.post('/login', data={
                    'email': 'test@example.com',
                    'password': 'testpassword'
                })
                
                # Test template creation
                template_data = {
                    'name': 'Test Template',
                    'description': 'Test template description',
                    'height_options': '170cm,180cm',
                    'hair_color_options': 'black,brown',
                    'eye_color_options': 'blue,green'
                }
                response = c.post('/create_template', data=template_data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                
                # Verify template creation
                template = CharacterTemplate.query.filter_by(user_id=user.id).first()
                self.assertIsNotNone(template)
                self.assertEqual(template.name, template_data['name'])
                
                # Test character creation
                response = c.post('/create_character', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                
                # Verify character creation
                character = Character.query.filter_by(user_id=user.id).first()
                self.assertIsNotNone(character)
                
                # Test character viewing
                response = c.get(f'/character/{character.id}')
                self.assertEqual(response.status_code, 200)
                
            logger.info("Character system test passed")
        except Exception as e:
            logger.error(f"Character system test failed: {str(e)}")
            raise

    # 4. Story Generation Tests
    def test_story_generation_system(self):
        """Test story generation with spiciness control"""
        logger.info("Testing story generation system...")
        try:
            # Create test data
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            user.spiciness_level = 1  # Set to family-friendly
            db.session.add(user)
            
            character = Character(
                name="Test Character",
                age=25,
                occupation="Tester",
                communication_style="Direct",
                user_id=user.id
            )
            db.session.add(character)
            
            scenario = Scenario(
                title="Test Scenario",
                description="Test description",
                setting="Test setting",
                challenge="Test challenge",
                goal="Test goal"
            )
            db.session.add(scenario)
            db.session.commit()
            
            # Test story generation
            story = generate_story_scene(character, scenario)
            self.assertIsInstance(story, dict)
            self.assertIn('introduction', story)
            self.assertIn('choices', story)
            
            # Test spiciness level control
            user.spiciness_level = 3  # Set to spicy
            db.session.commit()
            
            spicy_story = generate_story_scene(character, scenario)
            self.assertIsInstance(spicy_story, dict)
            self.assertIn('introduction', spicy_story)
            
            logger.info("Story generation test passed")
        except Exception as e:
            logger.error(f"Story generation test failed: {str(e)}")
            raise

    # 5. Photo Verification Tests
    def test_photo_verification_system(self):
        """Test photo verification and cleanup"""
        logger.info("Testing photo verification system...")
        try:
            # Create test image
            img_data = BytesIO()
            img_data.write(b"Test image data")
            img_data.seek(0)
            
            # Create test user and task
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            
            scenario = Scenario(
                title="Test Scenario",
                description="Test description"
            )
            db.session.add(scenario)
            
            task = ScavengerHuntTask(
                scenario_id=1,
                description="Test task",
                required_objects=json.dumps(['chair']),
                required_pose='hands_up'
            )
            db.session.add(task)
            db.session.commit()
            
            with self.client as c:
                # Login
                c.post('/login', data={
                    'email': 'test@example.com',
                    'password': 'testpassword'
                })
                
                # Test photo submission
                response = c.post(
                    f'/submit_task/{task.id}',
                    data={'photo': (img_data, 'test.jpg')},
                    content_type='multipart/form-data'
                )
                self.assertEqual(response.status_code, 302)
                
                # Verify submission was saved
                submission = TaskSubmission.query.filter_by(task_id=task.id).first()
                self.assertIsNotNone(submission)
                
            logger.info("Photo verification test passed")
        except Exception as e:
            logger.error(f"Photo verification test failed: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)
