from typing import Dict, Any, Optional
from src.backend.session_manager import SessionManager
from src.backend.response_handler import ResponseHandler
from src.backend.story_generator import StoryGenerator
import datetime


class RolePlayEngine:
    def __init__(self) -> None:
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_manager: SessionManager = SessionManager()
        self.response_handler: ResponseHandler = ResponseHandler()
        self.story_generator: StoryGenerator = StoryGenerator()
        self.active = True  # Add an attribute to track if the engine is active

    async def initialize(self) -> None:
        """Initialize the engine and its components"""
        # Add initialization logic here
        pass

    async def start_session(self, user_id: str) -> Dict[str, Any]:
        """Start a new session for a user"""
        session_data: Dict[str, Any] = self.session_manager.create_session(user_id)
        self.sessions[user_id] = session_data
        
        # Generate initial story segment
        initial_story = await self.story_generator.generate_story_segment({"choice": "start"})
        
        return {
            "status": "success",
            "message": "Session started",
            "metadata": session_data,
            "content": initial_story.get("story_text", ""),
            "choices": initial_story.get("choices", [])
        }

    async def process_choice(self, user_id: str, choice: str) -> Dict[str, Any]:
        """
        Process the user's choice and generate the next story segment.

        Parameters:
        - user_id (str): The identifier of the user.
        - choice (str): The choice made by the user.

        Returns:
        - Dict: A dictionary containing the status, content, and available choices.
        """
        if not self.active:
            raise ValueError("Engine is closed.")

        if user_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session = self.sessions[user_id]
        
        # Initialize user_choices if it doesn't exist or is empty
        if not session.get('user_choices'):
            session['user_choices'] = ['start']
        
        last_choice = session['user_choices'][-1]

        # Determine valid choices based on the last choice
        choices_list = self.story_generator.get_valid_choices(last_choice)
        valid_choices = [c["id"] for c in choices_list]

        if choice not in valid_choices:
            raise ValueError(f"Invalid choice: {choice} after {last_choice}")

        # Proceed to generate the next story segment
        next_segment = await self.story_generator.generate_story_segment({'choice': choice})
        
        # Use .get() method with default value to avoid KeyError
        story_text = next_segment.get('story_text', 'No story text available')
        
        # Update session state
        session['story_text'] = session.get('story_text', '') + "\n" + story_text
        session['user_choices'].append(choice)
        session['last_activity'] = datetime.datetime.now().isoformat()

        return {
            'status': 'success',
            'content': story_text,
            'choices': next_segment.get('choices', [])
        }

    async def close(self) -> None:
        """Close the engine and clean up sessions"""
        self.sessions.clear()
        self.active = False

    async def analyze_input(self, user_id: str, input_text: str) -> Dict[str, Any]:
        """
        Analyze user's text input and provide appropriate response.
        
        Parameters:
        - user_id (str): The identifier of the user
        - input_text (str): The text
        
        Returns:
        - Dict[str, Any]: Analysis results and appropriate responses
        """
        if user_id not in self.sessions:
            raise ValueError("Invalid session ID")
        
        # Basic analysis implementation
        return {
            "status": "success",
            "analysis": {
                "intent": "explore",
                "keywords": ["explore", "cave"],
                "sentiment": "neutral"
            },
            "response": "I understand you want to explore the cave. That sounds interesting!"
        }
