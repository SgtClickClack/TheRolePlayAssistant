import random

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn", "Robin", "Jamie"]
HEIGHTS = ["short", "average height", "tall", "very tall"]
HAIR_COLORS = ["brown", "black", "blonde", "red", "auburn", "silver", "midnight blue", "emerald green", 
               "starlight silver", "magical rainbow", "crystal white", "ethereal purple"]
EYE_COLORS = ["blue", "brown", "green", "hazel", "gray", "violet", "golden", "silver",
              "celestial blue", "mystic purple", "starlight gold", "crystal clear"]
STYLE_PREFERENCES = [
    "casual and comfortable", "sporty and athletic", "neat and classic", "creative and colorful", 
    "mystical and flowing", "royal and elegant", "nature-inspired", "magical academy uniform",
    "ethereal and dreamy", "celestial inspired", "enchanted forest style", "time traveler chic"
]
SIGNATURE_ITEMS = [
    "magic wand", "enchanted pendant", "mystical tome", "crystal compass", "friendship bracelet",
    "dragon scale charm", "fairy dust pouch", "phoenix feather quill",
    "time-turner necklace", "rune-inscribed bracelet", "starlight crystal", "dimensional key"
]

OCCUPATIONS = [
    # Original Occupations
    "Young Explorer", "Junior Scientist", "Art Student", "Music Scholar", 
    "Cooking Apprentice", "Nature Guide", "Space Cadet", "Animal Friend",
    "Apprentice Wizard", "Dragon Keeper", "Potion Maker", "Beast Tamer",
    "Forest Guardian", "Magic Librarian", "Royal Squire", "Fairy Garden Tender",
    "Junior Alchemist", "Monster Scholar", "Magical Artificer", "Crystal Healer",
    "Mystical Musician", "Dream Walker", "Star Whisperer", "Junior Enchanter",
    # New Fantasy Occupations
    "Dragon Tamer", "Spell Weaver", "Crystal Guardian", "Time Traveler",
    "Dream Walker", "Star Whisperer", "Ancient Rune Scholar", "Mystical Beast Keeper",
    "Celestial Navigator", "Portal Keeper", "Enchanted Artist", "Magical Zoologist"
]

COMMUNICATION_STYLES = [
    "friendly and outgoing", "thoughtful and gentle", "enthusiastic and energetic",
    "calm and patient", "cheerful and encouraging", "mystically wise",
    "dramatically theatrical", "mysteriously cryptic",
    "speaks in riddles", "communicates with magical gestures", 
    "telepathically empathetic", "timelessly eloquent"
]

CHALLENGE_HANDLING = [
    "breaks big problems into smaller steps",
    "asks friends for help when needed",
    "stays positive and keeps trying",
    "makes a plan before starting",
    "uses creativity to find solutions",
    "consults ancient tomes of wisdom",
    "seeks guidance from magical mentors",
    "meditates to find inner strength",
    "channels elemental energy",
    "consults with magical creatures",
    "reads the ancient runes",
    "uses prophetic visions"
]

HOBBIES = [
    "collecting magical crystals",
    "practicing simple spells",
    "tending magical plants",
    "studying mystical creatures",
    "brewing simple potions",
    "writing enchanted stories",
    "crafting magical items",
    "star chart mapping",
    "magical creature care",
    "enchanted art creation",
    "time stream surfing",
    "dimensional portal sketching",
    "rune stone collecting",
    "prophetic dream journaling"
]

QUIRKS = [
    "always carries a notebook for ideas",
    "gives names to all plants",
    "tells jokes when nervous",
    "hums while thinking",
    "collects interesting facts",
    "speaks to magical creatures",
    "glows slightly when excited",
    "floats when daydreaming",
    "makes sparkles when sneezing",
    "changes hair color with mood",
    "leaves magical footprints",
    "creates small illusions when happy",
    "understands ancient runes instinctively",
    "has prophetic dreams about small things",
    "controls minor elements when focused"
]

CHILDHOOD_STORIES = [
    # Original stories
    "Once organized a neighborhood cleanup day that turned into a weekly tradition",
    "Taught themselves to juggle using oranges from the family garden",
    "Built an amazing treehouse with help from their grandparents",
    "Started a reading club at school that's still going strong",
    "Rescued and cared for a lost kitten that became the family pet",
    # New fantasy backgrounds
    "Raised by a family of kind-hearted magical creatures in an enchanted forest",
    "Graduated top of their class from a prestigious mystical academy",
    "Born during a rare celestial event that occurs once every century",
    "Discovered a mysterious portal to another realm in their backyard",
    "Learned to speak with magical creatures at a young age",
    "First showed signs of magical ability during a full moon festival"
]

FAMILY_RELATIONS = [
    "Loves helping younger siblings with homework",
    "Bakes cookies every Sunday with grandma",
    "Goes camping with parents every summer",
    "Learns traditional songs from their aunts and uncles",
    "Shares a special hobby with their cousin",
    "Raised by wise forest creatures",
    "Mentored by ancient magical beings",
    "Connected to a lineage of time travelers",
    "Part of a family of dream keepers",
    "Descended from legendary crystal guardians"
]

LIFE_GOALS = [
    "Dreams of becoming a teacher to help others learn",
    "Wants to invent something that helps the environment",
    "Hopes to write and illustrate children's books",
    "Wishes to travel and make friends around the world",
    "Aims to start a community garden",
    "Aspires to master ancient magical arts",
    "Dreams of becoming a legendary creature guardian",
    "Hopes to discover new realms through portal magic",
    "Wishes to decode all ancient runes",
    "Plans to establish a sanctuary for magical creatures"
]

ACHIEVEMENTS = [
    "Won first prize in the science fair",
    "Organized a successful charity bake sale",
    "Learned to play three musical instruments",
    "Created a recycling program at school",
    "Taught their dog five amazing tricks",
    "Successfully tamed their first dragon",
    "Created their first stable portal",
    "Mastered the basics of elemental magic",
    "Decoded an ancient runic message",
    "Established communication with magical creatures"
]

COSTUMES = [
    {
        "main": "Enchanted Robes with glowing patterns",
        "accessories": ["crystal wand", "starlight pendant", "runic sash"],
        "alternatives": ["Celestial Mage outfit", "Dream Weaver robes", "Portal Master attire"]
    },
    {
        "main": "Mystical Armor with crystal accents",
        "accessories": ["energy shield", "power crystals", "enchanted gauntlets"],
        "alternatives": ["Battle Mage gear", "Guardian's armor", "Crystal Knight suit"]
    },
    {
        "main": "Nature Weaver's flowing garments",
        "accessories": ["living vine belt", "flower crown", "leaf-woven cape"],
        "alternatives": ["Forest Guardian attire", "Bloom Keeper robes", "Earth Mage outfit"]
    },
    {
        "main": "Time Traveler's steampunk attire",
        "accessories": ["chronometer watch", "dimensional goggles", "temporal compass"],
        "alternatives": ["Quantum Explorer suit", "Timekeeper robes", "Dimensional Drifter gear"]
    },
    {
        "main": "Star Mage's constellation cloak",
        "accessories": ["astral compass", "starlight staff", "moon phase medallion"],
        "alternatives": ["Celestial Sage robes", "Nova Weaver attire", "Cosmic Oracle garments"]
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
