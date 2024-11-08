import os
import openai
import logging
from typing import Dict, Any
from transformers import pipeline
from flask_login import current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients lazily
_openai_client = None
_hf_generator = None

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

def get_hf_generator():
    """Lazy initialization of Hugging Face pipeline"""
    global _hf_generator
    if _hf_generator is None:
        api_key = os.environ.get('HUGGINGFACE_API_KEY')
        if not api_key:
            logger.warning("Hugging Face API key not found in environment")
            return None
        try:
            _hf_generator = pipeline('text-generation',
                                  model='EleutherAI/gpt-j-6B',
                                  api_key=api_key)
            logger.info("Successfully initialized Hugging Face pipeline")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face pipeline: {str(e)}")
            return None
    return _hf_generator

def format_section(text: str) -> str:
    """Format text sections with proper line breaks and spacing"""
    return text.strip().replace('\n', ' ').replace('  ', ' ')

def get_spiciness_prompt(level: int) -> str:
    """Get the appropriate content style prompt based on spiciness level"""
    if level == 1:
        return (
            "You are a creative character developer focusing on family-friendly content. "
            "Keep all content suitable for all ages, avoiding any mature themes or references."
        )
    elif level == 2:
        return (
            "You are a creative character developer focusing on light romantic content. "
            "Include mild flirting and romantic themes, but keep it tasteful and appropriate. "
            "Avoid explicit content or mature themes."
        )
    else:  # level == 3
        return (
            "You are a creative character developer focusing on mature romantic content. "
            "Include romantic and spicy themes while maintaining good taste. "
            "Keep the content suggestive rather than explicit, focusing on tension and chemistry."
        )

def enhance_with_openai(prompt: str, spiciness_level: int) -> str:
    """Generate enhanced content using OpenAI GPT with spiciness control"""
    client = get_openai_client()
    if not client:
        return None
        
    try:
        system_prompt = get_spiciness_prompt(spiciness_level)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error with OpenAI generation: {str(e)}")
        return None

def enhance_with_huggingface(prompt: str) -> str:
    """Generate enhanced content using Hugging Face models."""
    generator = get_hf_generator()
    if not generator:
        return None
        
    try:
        response = generator(prompt,
                           max_length=1000,
                           num_return_sequences=1)
        return response[0]['generated_text']
    except Exception as e:
        logger.error(f"Error with Hugging Face generation: {str(e)}")
        return None

def generate_fallback_content(character: Dict[str, Any]) -> Dict[str, Any]:
    """Generate fallback content when both AI enhancements fail."""
    name = character['name']
    occupation = character['occupation'].lower()
    hobbies = character['hobbies']
    
    character['childhood_story'] = format_section(
        f"{name} grew up with a natural curiosity and passion for {hobbies}. "
        f"From an early age, they showed a keen interest in becoming a {occupation}, "
        "spending countless hours practicing and learning."
    )
    
    character['family_relations'] = format_section(
        f"{name} comes from a supportive family that encouraged their interests. "
        "They maintain close relationships with their parents and siblings, "
        "often sharing their achievements and experiences with them."
    )
    
    character['life_goals'] = format_section(
        f"As a dedicated {occupation}, {name} aims to excel in their field "
        f"while pursuing their passion for {hobbies}. They hope to inspire "
        "others and make a positive impact in their community."
    )
    
    character['achievements'] = format_section(
        f"{name} has earned recognition for their work as a {occupation}. "
        "Their dedication and unique approach have helped them overcome challenges "
        "and reach important milestones in both their personal and professional life."
    )
    
    return character

def parse_ai_response(content: str) -> Dict[str, str]:
    """Parse AI-generated content into structured sections."""
    sections = content.split('\n\n')
    result = {}
    
    for section in sections:
        section_lower = section.lower()
        if "childhood" in section_lower:
            result['childhood_story'] = format_section(section.split(':', 1)[1].strip() if ':' in section else section.strip())
        elif "family" in section_lower:
            result['family_relations'] = format_section(section.split(':', 1)[1].strip() if ':' in section else section.strip())
        elif "life goals" in section_lower or "aspiration" in section_lower:
            result['life_goals'] = format_section(section.split(':', 1)[1].strip() if ':' in section else section.strip())
        elif "achievement" in section_lower:
            result['achievements'] = format_section(section.split(':', 1)[1].strip() if ':' in section else section.strip())
    
    return result

def enhance_character_description(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance character descriptions using AI models.
    First tries OpenAI for controlled content generation,
    then falls back to Hugging Face for family-friendly content if needed.
    """
    # Get user's spiciness preference, default to family-friendly
    spiciness_level = getattr(current_user, 'spiciness_level', 1) if current_user.is_authenticated else 1
    
    prompt = f"""
    Please enhance and expand these character details in a creative way according to the specified content style:
    
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
    1. A detailed childhood story
    2. Description of family relationships and background
    3. Current life goals and aspirations
    4. Notable achievements and experiences
    
    Format each section with clear headers and proper spacing.
    """
    
    # Try OpenAI first with spiciness control
    logger.info(f"Attempting to enhance character with OpenAI (spiciness level: {spiciness_level})")
    if enhanced_content := enhance_with_openai(prompt, spiciness_level):
        sections = parse_ai_response(enhanced_content)
        if len(sections) >= 4:  # All required sections present
            character.update(sections)
            logger.info("Successfully enhanced character with OpenAI")
            return character
    
    # Fall back to Hugging Face (family-friendly only) if OpenAI fails
    if spiciness_level == 1:
        logger.info("Falling back to Hugging Face for family-friendly content")
        if enhanced_content := enhance_with_huggingface(prompt):
            sections = parse_ai_response(enhanced_content)
            if len(sections) >= 4:  # All required sections present
                character.update(sections)
                logger.info("Successfully enhanced character with Hugging Face")
                return character
    
    # Fall back to template generation if both AI methods fail
    logger.info("Using fallback content generation")
    return generate_fallback_content(character)
