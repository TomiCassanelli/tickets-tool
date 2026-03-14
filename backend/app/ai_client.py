from groq import Groq
from .config import get_env


def get_ai_client() -> Groq:
    """Return a Groq client configured from environment.

    The API key is read from the environment variable `GROQ_API_KEY`.
    """
    api_key = get_env('GROQ_API_KEY')
    return Groq(api_key=api_key)
