import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
TMDB_LANGUAGE = os.getenv("TMDB_LANGUAGE", "en-US")
TMDB_INCLUDE_ADULT = os.getenv("TMDB_INCLUDE_ADULT", "false").lower() == "true"
