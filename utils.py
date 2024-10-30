import random

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn", "Robin", "Jamie"]
HEIGHTS = ["short", "average height", "tall", "very tall"]
HAIR_COLORS = ["brown", "black", "blonde", "red", "auburn"]
EYE_COLORS = ["blue", "brown", "green", "hazel", "gray"]
STYLE_PREFERENCES = ["casual and comfortable", "sporty and athletic", "neat and classic", "creative and colorful"]
SIGNATURE_ITEMS = ["lucky charm bracelet", "favorite backpack", "special hat", "colorful glasses", "friendship necklace"]

OCCUPATIONS = [
    "Young Explorer", "Junior Scientist", "Art Student", "Music Scholar", 
    "Cooking Apprentice", "Nature Guide", "Space Cadet", "Animal Friend"
]

COMMUNICATION_STYLES = [
    "friendly and outgoing", "thoughtful and gentle", "enthusiastic and energetic",
    "calm and patient", "cheerful and encouraging"
]

CHALLENGE_HANDLING = [
    "breaks big problems into smaller steps",
    "asks friends for help when needed",
    "stays positive and keeps trying",
    "makes a plan before starting",
    "uses creativity to find solutions"
]

HOBBIES = [
    "collecting rocks and minerals",
    "building with blocks",
    "drawing comic books",
    "learning magic tricks",
    "growing plants",
    "stargazing",
    "making friendship bracelets",
    "writing stories"
]

QUIRKS = [
    "always carries a notebook for ideas",
    "gives names to all plants",
    "tells jokes when nervous",
    "hums while thinking",
    "collects interesting facts"
]

CHILDHOOD_STORIES = [
    "Once organized a neighborhood cleanup day that turned into a weekly tradition",
    "Taught themselves to juggle using oranges from the family garden",
    "Built an amazing treehouse with help from their grandparents",
    "Started a reading club at school that's still going strong",
    "Rescued and cared for a lost kitten that became the family pet"
]

FAMILY_RELATIONS = [
    "Loves helping younger siblings with homework",
    "Bakes cookies every Sunday with grandma",
    "Goes camping with parents every summer",
    "Learns traditional songs from their aunts and uncles",
    "Shares a special hobby with their cousin"
]

LIFE_GOALS = [
    "Dreams of becoming a teacher to help others learn",
    "Wants to invent something that helps the environment",
    "Hopes to write and illustrate children's books",
    "Wishes to travel and make friends around the world",
    "Aims to start a community garden"
]

ACHIEVEMENTS = [
    "Won first prize in the science fair",
    "Organized a successful charity bake sale",
    "Learned to play three musical instruments",
    "Created a recycling program at school",
    "Taught their dog five amazing tricks"
]

COSTUMES = [
    {
        "main": "Explorer's outfit with khaki vest and cargo pants",
        "accessories": ["compass necklace", "adventure hat", "binoculars"],
        "alternatives": ["Safari researcher", "Mountain climber", "Ocean explorer"]
    },
    {
        "main": "Scientist lab coat with safety goggles",
        "accessories": ["notebook and pencil", "magnifying glass", "experiment kit"],
        "alternatives": ["Space scientist", "Nature researcher", "Inventor"]
    },
    {
        "main": "Artist's smock with rainbow patterns",
        "accessories": ["paint brush set", "beret", "colorful scarf"],
        "alternatives": ["Street artist", "Museum curator", "Fashion designer"]
    }
]

def generate_character():
    costume_choice = random.choice(COSTUMES)
    
    return {
        "name": random.choice(NAMES),
        "age": random.randint(8, 14),
        "height": random.choice(HEIGHTS),
        "hair_color": random.choice(HAIR_COLORS),
        "eye_color": random.choice(EYE_COLORS),
        "style_preference": random.choice(STYLE_PREFERENCES),
        "signature_items": random.choice(SIGNATURE_ITEMS),
        "childhood_story": random.choice(CHILDHOOD_STORIES),
        "family_relations": random.choice(FAMILY_RELATIONS),
        "life_goals": random.choice(LIFE_GOALS),
        "achievements": random.choice(ACHIEVEMENTS),
        "occupation": random.choice(OCCUPATIONS),
        "communication_style": random.choice(COMMUNICATION_STYLES),
        "challenge_handling": random.choice(CHALLENGE_HANDLING),
        "hobbies": random.choice(HOBBIES),
        "quirks": random.choice(QUIRKS),
        "costume": costume_choice["main"],
        "accessories": ", ".join(costume_choice["accessories"]),
        "alternative_costumes": ", ".join(costume_choice["alternatives"])
    }

def generate_character_from_template(template):
    """Generate a character based on a template's options"""
    def get_random_option(options_str, default_list):
        if options_str and options_str.strip():
            options = [opt.strip() for opt in options_str.split(',')]
            return random.choice(options) if options else random.choice(default_list)
        return random.choice(default_list)

    return {
        "name": random.choice(NAMES),
        "age": random.randint(8, 14),
        "height": get_random_option(template.height_options, HEIGHTS),
        "hair_color": get_random_option(template.hair_color_options, HAIR_COLORS),
        "eye_color": get_random_option(template.eye_color_options, EYE_COLORS),
        "style_preference": get_random_option(template.style_preference_options, STYLE_PREFERENCES),
        "signature_items": get_random_option(template.signature_items_options, SIGNATURE_ITEMS),
        "childhood_story": get_random_option(template.childhood_story_templates, CHILDHOOD_STORIES),
        "family_relations": get_random_option(template.family_relations_templates, FAMILY_RELATIONS),
        "life_goals": get_random_option(template.life_goals_templates, LIFE_GOALS),
        "achievements": get_random_option(template.achievements_templates, ACHIEVEMENTS),
        "occupation": get_random_option(template.occupation_options, OCCUPATIONS),
        "communication_style": get_random_option(template.communication_style_options, COMMUNICATION_STYLES),
        "challenge_handling": get_random_option(template.challenge_handling_options, CHALLENGE_HANDLING),
        "hobbies": get_random_option(template.hobbies_options, HOBBIES),
        "quirks": get_random_option(template.quirks_options, QUIRKS),
        "costume": get_random_option(template.costume_options, [c["main"] for c in COSTUMES]),
        "accessories": get_random_option(template.accessories_options, 
                                      [', '.join(c["accessories"]) for c in COSTUMES]),
        "alternative_costumes": get_random_option(template.alternative_costumes_options,
                                                [', '.join(c["alternatives"]) for c in COSTUMES])
    }

SCENARIOS = [
    {
        "title": "The Lost Library",
        "description": "A magical library has appeared in town! Help find missing books and solve riddles.",
        "setting": "Ancient Library",
        "challenge": "Solve puzzles and find books",
        "goal": "Restore the library's magic"
    },
    {
        "title": "Space Adventure",
        "description": "Join a mission to explore a newly discovered planet!",
        "setting": "Outer Space",
        "challenge": "Navigate through asteroid fields",
        "goal": "Make first contact with friendly aliens"
    }
]

def get_random_scenario():
    return random.choice(SCENARIOS)