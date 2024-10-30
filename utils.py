import random

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn", "Robin", "Jamie", 
         "Charlie", "Avery", "Parker", "Drew", "Sydney"]

HEIGHTS = ["petite", "average height", "tall"]

HAIR_COLORS = ["brown", "black", "blonde", "red", "auburn", "gray", "dark brown", 
               "light brown", "honey blonde", "platinum blonde"]

EYE_COLORS = ["blue", "brown", "green", "hazel", "gray", "amber"]

STYLE_PREFERENCES = [
    "casual and comfortable", "sporty and athletic", "professional and polished", 
    "artistic and eclectic", "vintage inspired", "minimalist", "bohemian", 
    "streetwear", "preppy", "business casual"
]

SIGNATURE_ITEMS = [
    "vintage camera", "leather messenger bag", "colorful scarf", "classic watch",
    "sketchbook and pencils", "sports water bottle", "wireless headphones",
    "hiking boots", "leather jacket", "favorite sneakers", "gardening gloves",
    "chef's apron", "laptop bag", "reusable coffee cup"
]

OCCUPATIONS = [
    "Teacher", "Chef", "Photographer", "Artist", "Engineer", "Doctor", "Writer",
    "Architect", "Musician", "Personal Trainer", "Software Developer", "Nurse",
    "Journalist", "Interior Designer", "Environmental Scientist", "Film Director",
    "Dance Instructor", "Graphic Designer", "Veterinarian", "Travel Guide"
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
    "adapts quickly to changes",
    "focuses on solutions not problems",
    "takes calculated risks"
]

HOBBIES = [
    "hiking", "cooking", "painting", "playing guitar", "gardening",
    "photography", "yoga", "rock climbing", "writing poetry",
    "woodworking", "pottery", "surfing", "bird watching",
    "learning languages", "cycling", "camping", "dancing",
    "collecting vinyl records", "volunteering", "DIY home projects"
]

QUIRKS = [
    "always has a camera ready", "loves telling dad jokes", "hums while working",
    "collects interesting rocks", "names their plants", "always carries a book",
    "writes notes on coffee cups", "doodles during meetings",
    "remembers random facts", "loves trying new recipes",
    "speaks in movie quotes", "takes daily sunset photos",
    "organizes everything by color", "makes up songs about daily tasks",
    "always carries snacks"
]

CHILDHOOD_STORIES = [
    "Started a successful recycling program at school",
    "Won first place in the local art competition",
    "Organized a neighborhood cleanup day",
    "Founded a school photography club",
    "Built an award-winning science fair project",
    "Started a mini garden in the backyard",
    "Created a community book exchange",
    "Taught themselves to code at age 12",
    "Raised money for animal shelter through bake sales",
    "Led their school's environmental initiative"
]

FAMILY_RELATIONS = [
    "Weekly cooking sessions with grandparents",
    "Mountain biking with siblings every weekend",
    "Family game nights every Friday",
    "Gardening with parents",
    "Teaching tech skills to elderly relatives",
    "Annual family camping trips",
    "Morning jogs with cousins",
    "DIY projects with dad",
    "Cooking experiments with mom",
    "Photography walks with uncle"
]

LIFE_GOALS = [
    "Open a restaurant", "Publish a book", "Travel to every continent",
    "Start an eco-friendly business", "Run a marathon",
    "Learn three new languages", "Build a sustainable home",
    "Start a community art center", "Become a master chef",
    "Create a successful YouTube channel", "Open a photography studio",
    "Design sustainable fashion", "Start a coding bootcamp"
]

ACHIEVEMENTS = [
    "Won local photography contest",
    "Completed a marathon",
    "Published articles in magazines",
    "Started successful community project",
    "Earned advanced diving certification",
    "Mastered three musical instruments",
    "Created popular cooking blog",
    "Led successful fundraising campaign",
    "Developed popular mobile app",
    "Exhibited artwork in galleries"
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
    },
    {
        "main": "Chef's Professional Uniform",
        "accessories": ["professional knives", "recipe notebook", "timing watch"],
        "alternatives": ["Casual Cooking Wear", "Food Presentation Outfit", "Kitchen Training Gear"]
    },
    {
        "main": "Modern Tech Professional",
        "accessories": ["laptop bag", "wireless earbuds", "smart devices"],
        "alternatives": ["Remote Work Casual", "Tech Conference Wear", "Coding Session Outfit"]
    }
]

def generate_character():
    costume_choice = random.choice(COSTUMES)
    
    return {
        "name": random.choice(NAMES),
        "age": random.randint(18, 65),
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

    costume_choice = random.choice(COSTUMES)
    return {
        "name": random.choice(NAMES),
        "age": random.randint(18, 65),
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
