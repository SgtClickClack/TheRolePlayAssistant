import random

NAMES = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn", "Robin", "Jamie", 
         "Charlie", "Avery", "Parker", "Drew", "Sydney"]

HEIGHTS = ["petite", "average height", "tall"]

HAIR_COLORS = ["brown", "black", "blonde", "red", "auburn", "dark brown", 
               "light brown", "honey blonde", "platinum blonde"]

# Regular eye colors (90-95% chance)
EYE_COLORS = ["blue", "brown", "green", "hazel", "amber"]

# Function to get eye color with rare gray option
def get_eye_color():
    if random.random() < 0.08:  # 8% chance for gray eyes
        return "gray"
    return random.choice(EYE_COLORS)

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
    "Growing up in a small coastal town, they turned their parents' failing fish restaurant around by age 15. After watching their family struggle with debt, they learned to cook from YouTube videos, started a social media campaign, and brought in tourists from all over. The restaurant's signature dish? A recipe they discovered in their grandmother's old notebook.",
    "At 12, they survived being lost in the mountains for three days during a family camping trip. Using skills learned from wilderness books, they built a shelter, found water, and even helped rescue another lost hiker. That experience shaped their resilient spirit and passion for teaching survival skills.",
    "In their early teens, they transformed their family's dusty garage into a neighborhood art studio. What started as simple painting lessons for local kids evolved into a thriving community space where they organized art therapy sessions for seniors and at-risk youth. The annual art show they started still runs today, showcasing local talent and raising funds for art education.",
    "At 16, they developed an innovative recycling system for their school after watching their city's landfill grow. Through persistent advocacy and creative problem-solving, they implemented a program that reduced school waste by 70%. Their system became a model for other schools in the district, and they were invited to speak at environmental conferences while still in high school.",
    "Growing up with a deaf sibling, they created a revolutionary music visualization system at age 14. Using LED lights and vibration sensors, they built a way for their sister to 'feel' music. The project won the national science fair and sparked their lifelong dedication to accessible technology. Today, their prototype has evolved into a widely-used teaching tool in schools for the deaf."
]

FAMILY_RELATIONS = [
    "Every Sunday, they host an elaborate family dinner that's become legendary in their neighborhood. It started as a way to keep their immigrant grandparents' recipes alive, but has evolved into a weekly festival where three generations cook together, share stories, and teach the youngest family members about their heritage. They meticulously document each recipe and the story behind it in a family cookbook that's been growing for years.",
    "Their bond with their younger sibling transformed after their parents' divorce. Taking on the role of mentor and friend, they started a tradition of monthly adventure days, exploring new places and learning new skills together. From rock climbing to coding, these adventures not only strengthened their relationship but also helped both of them discover their passions and cope with change.",
    "As the first in their family to attend college, they developed a unique support system. Every Wednesday, they host virtual skill-sharing sessions where family members teach each other everything from traditional crafts to modern technology. Their grandmother teaches traditional weaving, while they teach digital marketing, creating a beautiful bridge between generations.",
    "After their father's health scare, they initiated a family fitness challenge that's lasted five years and counting. What began as morning walks evolved into family marathons, hiking expeditions, and dance classes. They've created a family blog documenting their journey from couch potatoes to fitness enthusiasts, inspiring other families in their community.",
    "Growing up in a multigenerational household, they became the family's cultural bridge. They translate not just languages but experiences, helping their grandparents navigate modern technology while teaching their younger cousins traditional customs. Their role has made them an exceptional mediator and storyteller, preserving family history through digital archives they create."
]

LIFE_GOALS = [
    "Start their own business helping others",
    "Travel to every continent",
    "Write a book about their experiences",
    "Create a community education program",
    "Build a sustainable eco-friendly home",
    "Start a mentorship program",
    "Open an art gallery featuring local artists",
    "Develop innovative teaching methods",
    "Create a wildlife sanctuary",
    "Establish a cultural exchange program"
]

ACHIEVEMENTS = [
    "Transformed a struggling local theater by launching an innovative community outreach program. They directed a series of plays featuring local stories, established youth workshops, and created a mentor system pairing experienced actors with newcomers. Within two years, the theater became a cultural hub, selling out shows and launching several successful careers in the arts.",
    "Pioneered a revolutionary urban farming initiative that turned abandoned lots into thriving community gardens. They developed a self-sustaining system where residents learn gardening skills, share produce, and sell at local markets. The project has been replicated in five other cities and has provided fresh food access to thousands of families.",
    "Created a groundbreaking language learning app that combines traditional teaching methods with augmented reality. Drawing from their experience teaching abroad, they developed an immersive system that helps users learn through real-world interactions. The app has reached over a million users and has been particularly successful in helping refugees adapt to new countries.",
    "Led a volunteer disaster response team that became a model for community emergency preparedness. After experiencing a natural disaster in their hometown, they organized and trained a network of neighborhood response units. Their system has been adopted by several cities and has demonstrably improved emergency response times.",
    "Developed an award-winning mentorship program connecting retired professionals with underprivileged students. The program has helped hundreds of students access higher education and career opportunities, while giving seniors a meaningful way to share their expertise. It's now being implemented nationwide through a network of community colleges."
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
    
    # Get character basics
    occupation = random.choice(OCCUPATIONS)
    childhood = random.choice(CHILDHOOD_STORIES)
    family = random.choice(FAMILY_RELATIONS)
    achievement = random.choice(ACHIEVEMENTS)
    
    # Create coherent background based on occupation and experiences
    character = {
        "name": random.choice(NAMES),
        "age": random.randint(18, 65),
        "height": random.choice(HEIGHTS),
        "hair_color": random.choice(HAIR_COLORS),
        "eye_color": get_eye_color(),  # Using the new eye color function
        "style_preference": random.choice(STYLE_PREFERENCES),
        "signature_items": random.choice(SIGNATURE_ITEMS),
        "occupation": occupation,
        "childhood_story": childhood,
        "family_relations": family,
        "life_goals": random.choice(LIFE_GOALS),
        "achievements": achievement,
        "communication_style": random.choice(COMMUNICATION_STYLES),
        "challenge_handling": random.choice(CHALLENGE_HANDLING),
        "hobbies": random.choice(HOBBIES),
        "quirks": random.choice(QUIRKS),
        "costume": costume_choice["main"],
        "accessories": ", ".join(costume_choice["accessories"]),
        "alternative_costumes": ", ".join(costume_choice["alternatives"])
    }
    
    return character

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
        "eye_color": get_eye_color(),  # Using the new eye color function
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
