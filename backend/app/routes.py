from fastapi import APIRouter, HTTPException
import json

from .models import TicketMetadata, TicketResponse, UserRequest
from .ai_client import get_ai_client

router = APIRouter()


def generar_markdown(metadata: TicketMetadata) -> str:
    criterios = "\n".join(f"- [ ] {c}" for c in metadata.criterios_de_aceptacion)
    return f"""# {metadata.titulo}

## Tipo: {metadata.tipo} | Prioridad: {metadata.prioridad}

### Contexto
{metadata.contexto}

### Criterios de Aceptación
{criterios}
"""


@router.post("/api/analyze-request", response_model=TicketResponse)
async def analyze_request(req: UserRequest):
    # Sistema: instrucciones para el LLM en ingles
    system_prompt = """
You are a strict Technical Product Owner. Your job is to receive an informal
request from a client or manager and convert it into a structured technical ticket.

Respond ONLY in valid JSON with these exact keys:
- "titulo": short and clear title
- "tipo": must be "Bug", "Feature" or "Task"
- "prioridad": must be "High", "Medium" or "Low"
- "contexto": technical context or detailed description
- "criterios_de_aceptacion": array of acceptance criteria strings

No extra text, no introductions — only the JSON object.
"""

    try:
        client = get_ai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.raw_text}
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            response_format={"type": "json_object"}
        )

        raw_response = chat_completion.choices[0].message.content
        if not raw_response:
            raise HTTPException(status_code=500, detail="Empty response from AI")
        ai_json = json.loads(raw_response)

        metadata = TicketMetadata(**ai_json)
        markdown = generar_markdown(metadata)

        return TicketResponse(metadata=metadata, markdown=markdown)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON response from AI")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
