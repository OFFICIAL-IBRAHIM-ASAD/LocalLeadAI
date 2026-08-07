from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database
DATABASE_PATH = BASE_DIR / "data" / "businesses.db"

# Browser
HEADLESS = False
SLOW_MO = 200

# Google Maps
GOOGLE_MAPS_URL = "https://www.google.com/maps"

# Timeouts (milliseconds)
PAGE_TIMEOUT = 60000
WAIT_AFTER_SEARCH = 5000
WAIT_AFTER_SCROLL = 2000

# Scraper
MAX_SCROLLS = 50
