import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def require_env(name, min_length=1):
    value = os.environ.get(name, "")
    if len(value) < min_length:
        raise RuntimeError(f"{name} must be set in the environment or .env (at least {min_length} characters)")
    return value


def env_int(name, default):
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise RuntimeError(f"{name} must be an integer, got '{value}'") from None


def env_bool(name, default=False):
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


JWT_SECRET = require_env("JWT_SECRET", min_length=32)
TOKEN_TTL_HOURS = env_int("TOKEN_TTL_HOURS", 5)
DB_PATH = Path(os.environ.get("DB_PATH") or Path(__file__).with_name("school.db"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = env_int("PORT", 5000)
DEBUG = env_bool("FLASK_DEBUG")
