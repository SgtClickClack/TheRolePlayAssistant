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
