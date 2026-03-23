import json
import logging
from typing import Union

from fastapi import APIRouter, HTTPException

from .models import (
    TicketMetadata,
    TicketResponse,
    UserRequest,
    ClarifyResponse,
    ClarificationRequest,
    ConversationTurn,
)
from .utils import generar_markdown
from .services.ticket_service import call_ai_and_parse
from .utils import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Router
router = APIRouter()

# Constants
MODEL_NAME = "llama-3.1-8b-instant"


def _build_conversation_prompt(raw_text: str, history: list[ConversationTurn]) -> str:
    """Build the prompt including conversation history for context."""
    prompt = raw_text
    
    if history:
        prompt += "\n\n--- Conversación previa ---\n"
        for turn in history:
            prompt += f"Pregunta: {turn.question}\nRespuesta: {turn.answer}\n"
    
    return prompt


@router.post("/api/analyze-request", response_model=Union[TicketResponse, ClarifyResponse])
async def analyze_request(req: UserRequest):
    """Receive raw text, ask the AI for structured ticket data, and return metadata + markdown.

    If the AI needs more information, it returns a clarifying question.
    The client can then send more conversation turns to continue clarifying.
    """
    try:
        prompt = _build_conversation_prompt(req.raw_text, [])
        ai_json = call_ai_and_parse(prompt, MODEL_NAME)

        if isinstance(ai_json, dict) and "clarifying_question" in ai_json:
            return ClarifyResponse(
                clarifying_question=ai_json["clarifying_question"],
                needs_more_clarification=ai_json.get("needs_more_clarification", True),
                conversation_context=ai_json.get("conversation_context", "")
            )

        metadata = TicketMetadata(**ai_json)
        markdown = generar_markdown(metadata)

        return TicketResponse(metadata=metadata, markdown=markdown, needs_more_clarification=False)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in analyze_request")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/continue-conversation", response_model=Union[TicketResponse, ClarifyResponse])
async def continue_conversation(req: ClarificationRequest):
    """Continue the conversation with the user's answer to a clarifying question.
    
    This endpoint allows multiple turns of conversation until the AI determines
    that it has enough information to create a complete ticket.
    """
    try:
        prompt = _build_conversation_prompt(req.raw_text, req.conversation_history)
        ai_json = call_ai_and_parse(prompt, MODEL_NAME)

        if isinstance(ai_json, dict) and "clarifying_question" in ai_json:
            return ClarifyResponse(
                clarifying_question=ai_json["clarifying_question"],
                needs_more_clarification=ai_json.get("needs_more_clarification", True),
                conversation_context=ai_json.get("conversation_context", "")
            )

        metadata = TicketMetadata(**ai_json)
        markdown = generar_markdown(metadata)

        return TicketResponse(metadata=metadata, markdown=markdown, needs_more_clarification=False)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in continue_conversation")
        raise HTTPException(status_code=500, detail="Internal server error")