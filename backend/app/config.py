from dotenv import load_dotenv
import os
from pathlib import Path


# Load .env from backend/ for local development if present
BASE_DIR = Path(__file__).resolve().parents[1]
DOTENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=DOTENV_PATH)


def get_env(key: str, default=None):
    return os.getenv(key, default)
