from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_MODEL = "gpt-4o-mini"
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "shipping.db"


def get_openai_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY") or None


def get_openai_model() -> str:
    return os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL
