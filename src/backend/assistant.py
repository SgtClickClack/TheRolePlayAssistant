from .story_generator import StoryGenerator
from .session_manager import SessionManager
from .response_handler import ResponseHandler
from ..api.api_handler import APIHandler


class RolePlayAssistant:
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.session_manager = SessionManager()
        self.response_handler = ResponseHandler()
        self.api_handler = APIHandler()

    async def start_session(self, user_id: str) -> dict:
        """Start new roleplay session"""
        session_id = self.session_manager.create_session(user_id)
        initial_story = await self.story_generator.generate_story_segment({})
        return {"session_id": session_id, "story": initial_story}
