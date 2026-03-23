from groq import Groq
from .config import settings


def get_ai_client() -> Groq:
    """Return a Groq client configured from environment.

    The API key is read from the environment variable `GROQ_API_KEY`.
    """
    return Groq(api_key=settings.GROQ_API_KEY)
