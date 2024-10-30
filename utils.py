import random
from collections import deque
import copy
from ai_generator import enhance_character_description

class TraitHistory:
    def __init__(self, max_history=3):
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        
    def add_character(self, character):
        self.history.append(character)
        
    def is_similar(self, new_traits, threshold=0.3):
        if not self.history:
            return False
            
        for old_char in self.history:
            similar_count = 0
            total_traits = 0
            
            for key, value in new_traits.items():
                if key in old_char and old_char[key] == value:
                    similar_count += 1
                total_traits += 1
                
            if similar_count / total_traits > threshold:
                return True
        return False

    def get_unused_option(self, options, key):
        if not self.history:
            return random.choice(options)
            
        used_options = {char[key] for char in self.history if key in char}
        unused_options = [opt for opt in options if opt not in used_options]
        
        if unused_options:
            return random.choice(unused_options)
        return random.choice(options)

# Initialize global trait history
trait_history = TraitHistory()

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn", "Robin", "Jamie", 
         "Charlie", "Avery", "Parker", "Drew", "Sydney"]

HEIGHTS = ["petite", "average height", "tall"]

HAIR_COLORS = ["brown", "black", "blonde", "red", "auburn", "dark brown", 
               "light brown", "honey blonde", "platinum blonde"]

EYE_COLORS = ["blue", "brown", "green", "hazel", "amber"]

def get_eye_color():
    if random.random() < 0.08:  # 8% chance for gray eyes
        return "gray"
    return trait_history.get_unused_option(EYE_COLORS, "eye_color")

STYLE_PREFERENCES = [
    "casual and comfortable", "sporty and athletic", "professional and polished", 
    "artistic and eclectic", "vintage inspired", "minimalist", "bohemian", 
    "streetwear", "preppy", "business casual"
]

SIGNATURE_ITEMS = [
    "vintage camera", "leather messenger bag", "colorful scarf", "classic watch",
    "sketchbook and pencils", "sports water bottle", "wireless headphones",
    "hiking boots", "leather jacket", "favorite sneakers"
]

OCCUPATIONS = [
    "Teacher", "Chef", "Photographer", "Artist", "Engineer", "Doctor", "Writer",
    "Architect", "Musician", "Personal Trainer", "Software Developer", "Nurse",
    "Journalist", "Interior Designer", "Environmental Scientist"
]

COMMUNICATION_STYLES = [
    "friendly and outgoing", "thoughtful and analytical", "enthusiastic and energetic",
    "calm and patient", "direct and confident", "creative and expressive",
    "empathetic and understanding", "professional and articulate"
]

CHALLENGE_HANDLING = [
    "breaks big problems into smaller steps",
    "researches thoroughly before starting",
    "seeks advice from mentors",
    "creates detailed action plans",
    "stays positive under pressure",
    "learns from past experiences",
    "collaborates with others",
    "adapts quickly to changes"
]

HOBBIES = [
    "hiking", "cooking", "painting", "playing guitar", "gardening",
    "photography", "yoga", "rock climbing", "writing poetry",
    "woodworking", "pottery", "surfing", "bird watching",
    "learning languages", "cycling"
]

QUIRKS = [
    "always has a camera ready", "loves telling dad jokes", "hums while working",
    "collects interesting rocks", "names their plants", "always carries a book",
    "writes notes on coffee cups", "doodles during meetings",
    "remembers random facts", "loves trying new recipes"
]

COSTUMES = [
    {
        "main": "Professional Business Attire",
        "accessories": ["leather briefcase", "smart watch", "classic tie"],
        "alternatives": ["Business Casual", "Conference Wear", "Meeting Attire"]
    },
    {
        "main": "Creative Studio Outfit",
        "accessories": ["canvas apron", "art supplies bag", "comfortable shoes"],
        "alternatives": ["Gallery Opening Attire", "Workshop Wear", "Paint Session Outfit"]
    },
    {
        "main": "Outdoor Adventure Gear",
        "accessories": ["hiking backpack", "water bottle", "trail map"],
        "alternatives": ["Climbing Gear", "Camping Outfit", "Trail Running Attire"]
    }
]

SCENARIOS = [
    {
        "title": "Community Garden Project",
        "description": "Help transform an empty lot into a thriving community garden!",
        "setting": "Urban Neighborhood",
        "challenge": "Organize volunteers and plan garden layout",
        "goal": "Create a sustainable green space"
    },
    {
        "title": "Local Food Festival",
        "description": "Organize and participate in the city's biggest food celebration!",
        "setting": "City Center",
        "challenge": "Coordinate with local restaurants and vendors",
        "goal": "Create unforgettable culinary experiences"
    },
    {
        "title": "Tech Startup Challenge",
        "description": "Build a team and create an innovative solution for local businesses!",
        "setting": "Modern Co-working Space",
        "challenge": "Develop and pitch a business idea",
        "goal": "Launch a successful startup"
    }
]

def get_random_scenario():
    return random.choice(SCENARIOS)

def generate_character():
    # Generate basic character
    character = {
        "name": trait_history.get_unused_option(NAMES, "name"),
        "age": random.randint(18, 65),
        "height": trait_history.get_unused_option(HEIGHTS, "height"),
        "hair_color": trait_history.get_unused_option(HAIR_COLORS, "hair_color"),
        "eye_color": get_eye_color(),
        "style_preference": trait_history.get_unused_option(STYLE_PREFERENCES, "style_preference"),
        "signature_items": trait_history.get_unused_option(SIGNATURE_ITEMS, "signature_items"),
        "occupation": trait_history.get_unused_option(OCCUPATIONS, "occupation"),
        "communication_style": trait_history.get_unused_option(COMMUNICATION_STYLES, "communication_style"),
        "challenge_handling": trait_history.get_unused_option(CHALLENGE_HANDLING, "challenge_handling"),
        "hobbies": trait_history.get_unused_option(HOBBIES, "hobbies"),
        "quirks": trait_history.get_unused_option(QUIRKS, "quirks")
    }
    
    # Enhance character with GPT
    enhanced_character = enhance_character_description(character)
    
    # Add costume details
    costume_choice = random.choice(COSTUMES)
    enhanced_character.update({
        "costume": costume_choice["main"],
        "accessories": ", ".join(costume_choice["accessories"]),
        "alternative_costumes": ", ".join(costume_choice["alternatives"])
    })
    
    # Check if character is too similar to recent ones
    max_attempts = 5
    attempts = 0
    while trait_history.is_similar(enhanced_character) and attempts < max_attempts:
        enhanced_character = generate_character()
        attempts += 1
    
    # Add to history if unique enough or max attempts reached
    trait_history.add_character(enhanced_character)
    return enhanced_character

def generate_character_from_template(template):
    def get_random_option(options_str, default_list):
        if options_str and options_str.strip():
            options = [opt.strip() for opt in options_str.split(',')]
            return random.choice(options) if options else random.choice(default_list)
        return random.choice(default_list)

    character = {
        "name": random.choice(NAMES),
        "age": random.randint(18, 65),
        "height": get_random_option(template.height_options, HEIGHTS),
        "hair_color": get_random_option(template.hair_color_options, HAIR_COLORS),
        "eye_color": get_eye_color(),
        "style_preference": get_random_option(template.style_preference_options, STYLE_PREFERENCES),
        "signature_items": get_random_option(template.signature_items_options, SIGNATURE_ITEMS),
        "occupation": get_random_option(template.occupation_options, OCCUPATIONS),
        "communication_style": get_random_option(template.communication_style_options, COMMUNICATION_STYLES),
        "challenge_handling": get_random_option(template.challenge_handling_options, CHALLENGE_HANDLING),
        "hobbies": get_random_option(template.hobbies_options, HOBBIES),
        "quirks": get_random_option(template.quirks_options, QUIRKS)
    }
    
    # Enhance character with GPT
    enhanced_character = enhance_character_description(character)
    
    # Add costume details
    enhanced_character.update({
        "costume": get_random_option(template.costume_options, [c["main"] for c in COSTUMES]),
        "accessories": get_random_option(template.accessories_options, 
                                      [', '.join(c["accessories"]) for c in COSTUMES]),
        "alternative_costumes": get_random_option(template.alternative_costumes_options,
                                                [', '.join(c["alternatives"]) for c in COSTUMES])
    })
    
    return enhanced_character
