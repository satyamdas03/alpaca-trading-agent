CITIES = {
    "india": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune"],
    "australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
}

CATEGORIES = [
    "cafe",
    "bakery",
    "salon",
    "gym",
    "retail shop",
    "plumber",
    "electrician",
    "restaurant",
]

SEARCH_TEMPLATES = {
    "cafe": "{category} in {city}",
    "bakery": "{category} in {city}",
    "salon": "hair {category} in {city}",
    "gym": "{category} in {city}",
    "retail shop": "{category} in {city}",
    "plumber": "{category} in {city}",
    "electrician": "{category} in {city}",
    "restaurant": "{category} in {city}",
}

MAX_RESULTS_PER_QUERY = 120

APOLLO_API_KEY = ""  # Set via env var APOLLO_API_KEY

OUTPUT_DIR = "output"
RAW_DIR = f"{OUTPUT_DIR}/raw"
ENRICHED_DIR = f"{OUTPUT_DIR}/enriched"
EXPORT_DIR = f"{OUTPUT_DIR}/exports"