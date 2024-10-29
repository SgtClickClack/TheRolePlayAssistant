import random

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn"]
OCCUPATIONS = ["Explorer", "Inventor", "Artist", "Musician", "Chef", "Teacher", "Scientist", "Astronaut"]
PERSONALITIES = ["Brave", "Creative", "Kind", "Curious", "Determined", "Friendly", "Helpful", "Wise"]
INTERESTS = ["Reading", "Music", "Art", "Science", "Nature", "Sports", "Cooking", "Space"]
COSTUMES = ["Cape and mask", "Lab coat", "Explorer's hat", "Chef's apron", "Artist's beret", "Space suit"]
ABILITIES = ["Flying", "Time freeze", "Animal communication", "Plant growing", "Weather control", "Healing"]

def generate_character():
    return {
        "name": random.choice(NAMES),
        "age": random.randint(8, 80),
        "occupation": random.choice(OCCUPATIONS),
        "personality": random.choice(PERSONALITIES),
        "interests": random.choice(INTERESTS),
        "costume": random.choice(COSTUMES),
        "special_ability": random.choice(ABILITIES)
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
