import os
import logging
import openai
from typing import Dict, Any, List
from models import Character, Scenario
from flask_login import current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
_openai_client = None

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found in environment")
            return None
        try:
            _openai_client = openai.Client(api_key=api_key)
            logger.info("Successfully initialized OpenAI client")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return None
    return _openai_client

def get_story_prompt(character: Character, scenario: Scenario) -> str:
    """Generate a story prompt based on character and scenario"""
    return f"""Create an engaging story scene for a role-playing scenario with the following details:

Character:
- Name: {character.name}
- Age: {character.age}
- Occupation: {character.occupation}
- Personality: {character.communication_style}
- Background: {character.childhood_story}

Scenario:
- Title: {scenario.title}
- Setting: {scenario.setting}
- Challenge: {scenario.challenge}
- Goal: {scenario.goal}

Create a dynamic scene that:
1. Introduces the character in the setting
2. Presents the challenge in an engaging way
3. Provides 2-3 possible choices/actions for the character
4. Describes potential consequences for each choice

Keep the tone appropriate for the character's personality and background.
Make the scene interactive and engaging, focusing on character development and meaningful choices.
"""

def get_spiciness_prompt(level: int) -> str:
    """Get content style prompt based on spiciness level"""
    if level == 1:
        return (
            "You are creating family-friendly role-playing content. "
            "Keep all content suitable for all ages, avoiding any mature themes or references."
        )
    elif level == 2:
        return (
            "You are creating mild romantic role-playing content. "
            "Include light flirting and romantic themes, but keep it tasteful and appropriate. "
            "Avoid explicit content or mature themes."
        )
    else:  # level == 3
        return (
            "You are creating spicy romantic role-playing content. "
            "Include romantic and spicy themes while maintaining good taste. "
            "Keep the content suggestive rather than explicit, focusing on tension and chemistry."
        )

def generate_story_scene(character: Character, scenario: Scenario) -> Dict[str, Any]:
    """Generate a dynamic story scene using AI"""
    client = get_openai_client()
    if not client:
        logger.error("OpenAI client not initialized")
        return generate_fallback_scene(character, scenario)

    try:
        # Get user's spiciness preference or default to family-friendly
        spiciness_level = getattr(current_user, 'spiciness_level', 1) if current_user.is_authenticated else 1
        
        # Generate story content
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": get_spiciness_prompt(spiciness_level)},
                {"role": "user", "content": get_story_prompt(character, scenario)}
            ],
            max_tokens=1000,
            temperature=0.8
        )
        
        story_content = response.choices[0].message.content
        
        # Parse the content into sections
        sections = parse_story_content(story_content)
        return sections
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return generate_fallback_scene(character, scenario)

def parse_story_content(content: str) -> Dict[str, Any]:
    """Parse AI-generated content into structured sections"""
    try:
        # Split content into sections
        parts = content.split('\n\n')
        
        # Initialize sections
        scene = {
            'introduction': '',
            'challenge': '',
            'choices': [],
            'consequences': {}
        }
        
        current_section = 'introduction'
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if 'choice' in part.lower() or 'option' in part.lower():
                # Extract choice
                choice = part.split(':')[-1].strip()
                scene['choices'].append(choice)
                current_section = 'choices'
            elif 'consequence' in part.lower() or 'outcome' in part.lower():
                # Extract consequence for the last choice
                if scene['choices']:
                    last_choice = scene['choices'][-1]
                    scene['consequences'][last_choice] = part.split(':')[-1].strip()
            elif current_section == 'introduction':
                scene['introduction'] = part
                current_section = 'challenge'
            elif current_section == 'challenge':
                scene['challenge'] = part
        
        return scene
        
    except Exception as e:
        logger.error(f"Error parsing story content: {str(e)}")
        return {
            'introduction': content,
            'challenge': '',
            'choices': [],
            'consequences': {}
        }

def generate_fallback_scene(character: Character, scenario: Scenario) -> Dict[str, Any]:
    """Generate a basic scene when AI generation fails"""
    return {
        'introduction': (
            f"{character.name}, a {character.age}-year-old {character.occupation}, "
            f"finds themselves in {scenario.setting}. "
            f"With their {character.communication_style} nature, they approach the situation cautiously."
        ),
        'challenge': scenario.challenge,
        'choices': [
            "Face the challenge head-on",
            "Look for an alternative solution",
            "Seek help from others"
        ],
        'consequences': {
            "Face the challenge head-on": "A direct approach might lead to immediate results but could be risky.",
            "Look for an alternative solution": "Taking time to find another way might be safer but could take longer.",
            "Seek help from others": "Working with others could provide more resources but might complicate the situation."
        }
    }
