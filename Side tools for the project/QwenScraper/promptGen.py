import random

# Core categories for non-repeating trivia generation
TRIVIA_TOPICS = [
    "cryptic symbiotic relationships", "quantum biology anomalies",
    "xenobiotic hyperaccumulation", "electromagnetic adaptations",
    "lunar/tidal synchronization", "horizontal gene transfer oddities",
    "bioluminescent deception", "cryogenic survival mechanisms",
    "metal-accumulating marvels", "acoustic signaling systems"
]

SCIENTIFIC_ANGLES = [
    "epigenetic hybridization", "nanoscale biophotonics",
    "radioresistant metabolites", "magnetoreceptive root systems",
    "time-dilated flowering", "metalloenzyme catalysis",
    "phonon-mediated transport", "quantum tunneling"
]

GEOGRAPHIC_FILTERS = [
    "Madagascar-only species", "Andean cloud forest flora",
    "Antarctic extremophiles", "Socotra Island endemics",
    "New Caledonia nickel hyperaccumulators", "Sahara subterranean flora"
]

EXCLUSIONS = [
    "No carnivorous plants", "Avoid angiosperms",
    "Exclude Amazon basin species", "No fungal symbiosis",
    "No photosynthesis-related adaptations"
]

# Structure specifically for 10-item trivia lists
STRUCTURE = "List 10 [TOPIC] plant facts that challenge [ANGLE] theories, [EXCLUSION], and [GEOGRAPHIC] focus."

def generate_trivia_prompt():
    # Randomly combine elements
    topic = random.choice(TRIVIA_TOPICS)
    angle = random.choice(SCIENTIFIC_ANGLES)
    exclusion = random.choice(EXCLUSIONS)
    region = random.choice(GEOGRAPHIC_FILTERS)
    
    # Build the prompt
    prompt = STRUCTURE.replace("[TOPIC]", topic)
    prompt = prompt.replace("[ANGLE]", angle)
    prompt = prompt.replace("[EXCLUSION]", exclusion)
    prompt = prompt.replace("[GEOGRAPHIC]", region)
    
    return prompt
