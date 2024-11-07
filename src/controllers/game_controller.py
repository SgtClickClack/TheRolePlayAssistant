from typing import Dict, Optional, Any
from ..api.story_generator import StoryGenerator    
from datetime import datetime

class GameController:
    def __init__(self):
        self.story_generator = StoryGenerator()
        self.active_sessions = {}  # Store active game sessions

    def start_game(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new game session.
        
        Args:
            user_id: Unique identifier for the user
            preferences: Dictionary containing game preferences
            
        Returns:
            Dict containing game session information
        """
        try:
            # Generate a new story
            story = self.story_generator.generate_story(preferences)
            
            # Create game session
            session = {
                'user_id': user_id,
                'story': story,
                'items_found': [],
                'start_time': datetime.now(),
                'current_clue_index': 0,
                'completed': False
            }
            
            self.active_sessions[user_id] = session
            
            return {
                'status': 'success',
                'story_title': story['title'],
                'first_clue': self.story_generator.generate_clues(story)[0],
                'total_items': len(story['items'])
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def verify_item(self, user_id: str, image_data: bytes) -> Dict:
        """Verify uploaded image matches current item."""
        session = self.active_sessions.get(user_id)
        if not session:
            return {'status': 'error', 'message': 'No active game session'}

        current_item = session['story']['items'][session['current_clue_index']]
        
        # For demo, always return success
        verification_result = self.story_generator.verify_item(image_data, current_item)
        
        if verification_result:
            session['items_found'].append(current_item)
            session['current_clue_index'] += 1
            
            # Check if game is completed
            if session['current_clue_index'] >= len(session['story']['items']):
                session['completed'] = True
                return self._generate_completion_response(session)
            
            # Generate next clue
            next_clue = self.story_generator.generate_clues(session['story'])[session['current_clue_index']]
            
            return {
                'status': 'success',
                'message': 'Item found!',
                'next_clue': next_clue,
                'progress': self.story_generator.generate_story_progression(session['story'], session['items_found'])
            }
        else:
            return {'status': 'error', 'message': 'Item not found'}

    def _generate_completion_response(self, session: Dict) -> Dict:
        # Implement your completion response logic here
        pass 