import os
from dotenv import load_dotenv

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file if it exists
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

# Database configuration (Switch to PostgreSQL/MySQL via ENV in production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voice_auth.db")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-voice-key-12345-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HuggingFace & SpeechBrain configurations for Windows compatibility
# Disable symlinks for HuggingFace caching to avoid admin privileges issues on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# Temporary audio processing folder
TEMP_AUDIO_DIR = os.path.join(BASE_DIR, "temp_audio")
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
