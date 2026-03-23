import json
import logging

from ..core.ai_client import get_ai_client
from ..utils import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def call_ai_and_parse(raw_text: str, model_name: str, temperature: float = 0.0) -> dict:
    """Llama al cliente AI con el `SYSTEM_PROMPT` y devuelve el JSON parseado.

    Lanza excepciones en caso de fallos para que el router las transforme en HTTPException.
    """
    client = get_ai_client()
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_text},
            ],
            model=model_name,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.exception("Fallo en la petición al cliente AI")
        raise

    try:
        raw_content = response.choices[0].message.content
    except Exception:
        logger.exception("Respuesta inesperada del AI: estructura inválida")
        raise

    if not raw_content:
        raise ValueError("Respuesta vacía del AI")

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        logger.exception("El AI devolvió JSON inválido")
        raise
