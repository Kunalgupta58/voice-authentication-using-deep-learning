import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env locally — HF Spaces / Render inject env vars directly
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))


def _normalize_database_url(url: str) -> str:
    """Render and Neon both emit postgres:// — SQLAlchemy needs postgresql://"""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DB_URL")
    or "sqlite:///./voice_auth.db"
)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import secrets
    import logging
    logging.getLogger(__name__).warning(
        "SECRET_KEY not set — generating a random key. "
        "All JWTs will be invalidated on restart. Set SECRET_KEY in Space secrets."
    )
    SECRET_KEY = secrets.token_hex(32)

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# HuggingFace / SpeechBrain
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp")

# Temp audio dir — use /tmp so it's always writable (even under non-root HF Spaces user)
TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", "/tmp/voicekey_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
