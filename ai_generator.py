import os
import openai
from typing import Dict, Any

# Initialize OpenAI client with API key from environment
client = openai.Client(api_key=os.environ.get('OPENAI_API_KEY'))

def enhance_character_description(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance character descriptions using GPT to make them more creative and detailed.
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
    1. An enhanced childhood story (family-friendly)
    2. A detailed family background
    3. Unique life goals and achievements
    4. A vivid description of their current lifestyle
    Keep everything appropriate for all ages.
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
            if "childhood story" in section.lower():
                character['childhood_story'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "family background" in section.lower():
                character['family_relations'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "life goals" in section.lower():
                character['life_goals'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
            elif "achievements" in section.lower():
                character['achievements'] = section.split(':', 1)[1].strip() if ':' in section else section.strip()
        
        return character
        
    except Exception as e:
        print(f"Error enhancing character with GPT: {str(e)}")
        return character  # Return original character if enhancement fails
