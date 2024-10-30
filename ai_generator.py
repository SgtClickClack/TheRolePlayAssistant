import os
import openai
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key from environment
client = openai.Client(api_key=os.environ.get('OPENAI_API_KEY'))

def generate_fallback_content(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate fallback content when the AI enhancement fails.
    """
    name = character['name']
    occupation = character['occupation'].lower()
    hobbies = character['hobbies']
    
    # Generate basic backstory templates
    character['childhood_story'] = (
        f"{name} grew up with a natural curiosity and passion for {hobbies}. "
        f"From an early age, they showed a keen interest in becoming a {occupation}, "
        "spending countless hours practicing and learning."
    )
    
    character['family_relations'] = (
        f"{name} comes from a supportive family that encouraged their interests. "
        "They maintain close relationships with their parents and siblings, "
        "often sharing their achievements and experiences with them."
    )
    
    character['life_goals'] = (
        f"As a dedicated {occupation}, {name} aims to excel in their field "
        f"while pursuing their passion for {hobbies}. They hope to inspire "
        "others and make a positive impact in their community."
    )
    
    character['achievements'] = (
        f"{name} has earned recognition for their work as a {occupation}. "
        "Their dedication and unique approach have helped them overcome challenges "
        "and reach important milestones in both their personal and professional life."
    )
    
    return character

def enhance_character_description(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance character descriptions using GPT to make them more creative and detailed.
    Falls back to template-based generation if AI enhancement fails.
    """
    # Create a prompt for GPT to enhance the character
    prompt = f"""
    Please enhance and expand these character details in a creative, family-friendly way:
    
    Name: {character['name']}
    Age: {character['age']}
    Occupation: {character['occupation']}
    
    Current traits:
    - Appearance: {character['height']}, {character['hair_color']} hair, {character['eye_color']} eyes
    - Style: {character['style_preference']}
    - Personality: Communicates in a {character['communication_style']} way
    - Hobbies: {character['hobbies']}
    - Quirks: {character['quirks']}
    
    Please provide:
    1. A detailed childhood story (family-friendly)
    2. Description of family relationships and background
    3. Current life goals and aspirations
    4. Notable achievements and experiences
    
    Keep everything appropriate for all ages and focus on positive, uplifting content.
    """
    
    try:
        # Generate enhanced content using GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative character developer focusing on family-friendly content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract the generated content
        enhanced_content = response.choices[0].message.content
        
        # Parse the enhanced content and update character details
        sections = enhanced_content.split('\n\n')
        for section in sections:
            section_lower = section.lower()
            if "childhood" in section_lower:
                character['childhood_story'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "family" in section_lower:
                character['family_relations'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "life goals" in section_lower or "aspiration" in section_lower:
                character['life_goals'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "achievement" in section_lower:
                character['achievements'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
        
        # Verify all required fields are present
        required_fields = ['childhood_story', 'family_relations', 'life_goals', 'achievements']
        if not all(field in character for field in required_fields):
            logger.warning("Some fields missing from GPT response, using fallback content")
            return generate_fallback_content(character)
            
        return character
        
    except Exception as e:
        logger.error(f"Error enhancing character with GPT: {str(e)}")
        logger.info("Using fallback content generation")
        return generate_fallback_content(character)
