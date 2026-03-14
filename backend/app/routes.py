from fastapi import APIRouter, HTTPException
import json

from .models import Ticket, UserRequest
from .ai_client import get_ai_client

router = APIRouter()


@router.post("/api/analyze-request", response_model=Ticket)
async def analyze_request(req: UserRequest):
    system_prompt = """
    You are a strict Technical Product Owner. Your job is to receive an informal
    request from a client or manager and convert it into a structured technical ticket.

    Respond ONLY in valid JSON using exactly these keys:
    "title", "description", "type", "priority".
    No extra text, no introductions — only the JSON object.
    """

    try:
        client = get_ai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.raw_text}
            ],
            model="groq/compound",
            temperature=0,
            response_format={"type": "json_object"}
        )

        raw_response = chat_completion.choices[0].message.content
        ai_json = json.loads(raw_response)

        return Ticket(**ai_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
