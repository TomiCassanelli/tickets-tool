from groq import Groq
from .config import settings


def get_ai_client() -> Groq:
    """Return a Groq client configured from environment.

    The API key is read from the environment variable `GROQ_API_KEY`.
    """
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is required when AI_OFFLINE_MODE is disabled")
    return Groq(api_key=settings.GROQ_API_KEY)
