import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def require_env(name, min_length=1):
    value = os.environ.get(name, "")
    if len(value) < min_length:
        raise RuntimeError(f"{name} must be set in the environment or .env (at least {min_length} characters)")
    return value


JWT_SECRET = require_env("JWT_SECRET", min_length=32)
