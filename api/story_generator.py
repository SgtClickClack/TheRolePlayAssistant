import random
from typing import Dict, List

class StoryGenerator:
    def __init__(self):
        self.story_templates = {
            'beginner': [
                {
                    'title': 'Backyard Adventure',
                    'items': ['tree', 'flower', 'bird'],
                    'difficulty': 1
                },
                {
                    'title': 'Home Discovery',
                    'items': ['book', 'chair', 'window'],
                    'difficulty': 1
                }
            ],
            'intermediate': [
                {
                    'title': 'Urban Explorer',
                    'items': ['building', 'street sign', 'bicycle'],
                    'difficulty': 2
                }
            ],
            'advanced': [
                {
                    'title': 'Nature Detective',
                    'items': ['specific tree species', 'wildlife', 'landscape feature'],
                    'difficulty': 3
                }
            ]
        }
        
    def generate_story(self, preferences: Dict) -> Dict:
        """Generate a personalized story based on user preferences."""
        try:
            # Select appropriate difficulty level
            difficulty = self._determine_difficulty(preferences)
            available_stories = self._filter_stories(difficulty)
            
            if not available_stories:
                raise ValueError("No suitable stories found for given preferences")
            
            return random.choice(available_stories)
            
        except Exception as e:
            raise ValueError(f"Failed to generate story: {str(e)}")
    
    def _determine_difficulty(self, preferences: Dict) -> str:
        """Determine story difficulty based on user preferences and experience."""
        experience_level = preferences.get('experience_level', 'beginner')
        age = preferences.get('age', 0)
        
        if age < 8 or experience_level == 'beginner':
            return 'beginner'
        elif age < 12 or experience_level == 'intermediate':
            return 'intermediate'
        else:
            return 'advanced'
    
    def _filter_stories(self, difficulty: str) -> List[Dict]:
        """Filter stories based on difficulty level."""
        return self.story_templates.get(difficulty, [])
    
    def generate_clues(self, story: Dict) -> List[str]:
        """Generate clues for items in the story."""
        clues = []
        for item in story['items']:
            clue = self._create_clue(item)
            clues.append(clue)
        return clues
    
    def _create_clue(self, item: str) -> str:
        """Create an engaging clue for a specific item."""
        clue_templates = [
            f"Can you find something that looks like a {item}?",
            f"Your next discovery should be a {item}!",
            f"Look around for a {item} - it might be closer than you think!",
            f"Time to search for a {item} in your surroundings."
        ]
        return random.choice(clue_templates)

    def generate_story_progression(self, story: Dict, items_found: List[str]) -> Dict:
        """Track story progression and generate appropriate feedback."""
        total_items = len(story['items'])
        found_items = len(items_found)
        progress_percentage = (found_items / total_items) * 100

        progression = {
            'total_items': total_items,
            'found_items': found_items,
            'progress_percentage': progress_percentage,
            'remaining_items': [item for item in story['items'] if item not in items_found],
            'status': self._get_progress_status(progress_percentage),
            'rewards': self._calculate_rewards(progress_percentage, story['difficulty'])
        }
        
        return progression

    def _get_progress_status(self, progress_percentage: float) -> str:
        """Determine the status message based on progress."""
        if progress_percentage == 0:
            return "Just getting started! Ready for an adventure?"
        elif progress_percentage < 50:
            return "You're making progress! Keep exploring!"
        elif progress_percentage < 99:
            return "Almost there! Just a few more discoveries to make!"
        else:
            return "Congratulations! You've completed the adventure!"

    def _calculate_rewards(self, progress_percentage: float, difficulty: int) -> Dict:
        """Calculate rewards based on progress and difficulty."""
        base_points = difficulty * 100
        progress_multiplier = progress_percentage / 100
        
        rewards = {
            'points': int(base_points * progress_multiplier),
            'badges': self._determine_badges(progress_percentage, difficulty),
            'achievements': self._check_achievements(progress_percentage, difficulty)
        }
        
        return rewards

    def _determine_badges(self, progress_percentage: float, difficulty: int) -> List[str]:
        """Award badges based on progress and difficulty."""
        badges = []
        
        if progress_percentage >= 25:
            badges.append("Explorer")
        if progress_percentage >= 50:
            badges.append("Adventurer")
        if progress_percentage >= 75:
            badges.append("Discoverer")
        if progress_percentage == 100:
            badges.append(f"Level {difficulty} Master")
            
        return badges

    def _check_achievements(self, progress_percentage: float, difficulty: int) -> List[str]:
        """Check and award achievements based on progress and difficulty."""
        achievements = []
        
        if difficulty >= 2 and progress_percentage == 100:
            achievements.append("Expert Explorer")
        if difficulty >= 3 and progress_percentage >= 75:
            achievements.append("Master Detective")
        if progress_percentage == 100:
            achievements.append(f"Completed {self._get_difficulty_name(difficulty)} Adventure")
            
        return achievements

    def _get_difficulty_name(self, difficulty: int) -> str:
        """Convert difficulty level to string name."""
        difficulty_names = {
            1: "Beginner",
            2: "Intermediate",
            3: "Advanced"
        }
        return difficulty_names.get(difficulty, "Unknown")