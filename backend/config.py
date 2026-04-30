import os
from dotenv import load_dotenv

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file if it exists
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

# Database configuration (Switch to PostgreSQL/MySQL via ENV in production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voice_auth.db")

# SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-voice-key-12345-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HuggingFace & SpeechBrain configurations for Windows compatibility
# Disable symlinks for HuggingFace caching to avoid admin privileges issues on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# Temporary audio processing folder
default_temp_dir = os.path.join(BASE_DIR, "temp_audio") if os.name == "nt" else "/tmp/voicekey_temp_audio"
TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", default_temp_dir)
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
