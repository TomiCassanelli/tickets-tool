import json
import logging
from typing import Dict, Any, Optional, List

from ..core.ai_client import get_ai_client
from ..core.config import settings
from ..models import (
    TicketSession, Message, AgenticResponse, ToolCallingMeta, 
    TicketMetadata, GenerateResponseData, ReviseResponseData
)
from ..repository import TicketRepository
from ..state_machine import TicketStatus, transition_ticket, InvalidStateException
from ..prompts import ANALYSIS_PROMPT, GENERATION_PROMPT, REVISION_PROMPT
from .exceptions import AIServiceError

logger = logging.getLogger(__name__)

def _build_v1_history_prompt(session: TicketSession) -> str:
    """Combines conversation history into a single text block for the LLM context."""
    prompt = ""
    for msg in session.history:
        if msg.role == "user":
            prompt += f"Usuario: {msg.content}\n"
        elif msg.role == "assistant":
            prompt += f"Asistente: {msg.content}\n"
    return prompt

def _call_analysis_ai(session: TicketSession) -> Dict[str, Any]:
    """Calls the AI to analyze the current session and determine if it's ready."""
    prompt = _build_v1_history_prompt(session)
    client = get_ai_client()
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": prompt},
            ],
            model=settings.AI_MODEL_NAME,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.exception("Fallo en la petición al cliente AI (V1 Analysis)")
        raise AIServiceError("Error communicating with AI provider") from e

    try:
        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValueError("Empty response")
        return json.loads(raw_content)
    except Exception as e:
        logger.exception("Respuesta inesperada del AI en V1 Analysis")
        raise AIServiceError("Invalid response structure from AI") from e

def _create_agentic_response(session: TicketSession, action: str, next_questions: Optional[List[str]] = None, data: Any = None) -> AgenticResponse:
    """Helper to construct the standardized ToolCallingMeta response."""
    next_actions = []
    if next_questions is None:
        next_questions = []
    if session.status == TicketStatus.NEEDS_CLARIFICATION:
        next_actions = [f"/api/tickets/{session.id}/clarifications"]
    elif session.status == TicketStatus.READY_TO_GENERATE:
        next_actions = [f"/api/tickets/{session.id}/generate"]
    elif session.status == TicketStatus.GENERATED:
        next_actions = [f"/api/tickets/{session.id}/revise", f"/api/tickets/{session.id}/finalize"]
        
    meta = ToolCallingMeta(
        ticket_id=session.id,
        status=session.status,
        action=action,
        next_allowed_actions=next_actions,
        missing_context_fields=session.missing_context_fields,
        next_questions=next_questions or []
    )
    return AgenticResponse(meta=meta, data=data)

def process_intake(prompt: str, repo: TicketRepository) -> AgenticResponse:
    """Handles the initial intake of a ticket request."""
    session = TicketSession()
    session.history.append(Message(role="user", content=prompt))
    
    analysis_result = _call_analysis_ai(session)
    is_ready = analysis_result.get("is_ready", False)
    missing_fields = analysis_result.get("missing_context_fields", [])
    next_questions = analysis_result.get("next_questions", [])
    
    if is_ready:
        session.status = transition_ticket(session.status, TicketStatus.READY_TO_GENERATE)
    else:
        session.status = transition_ticket(session.status, TicketStatus.NEEDS_CLARIFICATION)
        session.missing_context_fields = missing_fields
        # Append assistant questions to history
        if next_questions:
            session.history.append(Message(role="assistant", content=" ".join(next_questions)))
            
    repo.save(session)
    return _create_agentic_response(session, "intake_processed", next_questions)

def process_clarification(ticket_id: str, answer: str, repo: TicketRepository) -> AgenticResponse:
    """Handles user clarification answers."""
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")
        
    # Validation
    if session.status not in [TicketStatus.NEEDS_CLARIFICATION, TicketStatus.READY_TO_GENERATE]:
        raise InvalidStateException(f"Cannot clarify a ticket in {session.status.value} state")

    session.history.append(Message(role="user", content=answer))
    
    analysis_result = _call_analysis_ai(session)
    is_ready = analysis_result.get("is_ready", False)
    missing_fields = analysis_result.get("missing_context_fields", [])
    next_questions = analysis_result.get("next_questions", [])
    
    if is_ready:
        session.status = transition_ticket(session.status, TicketStatus.READY_TO_GENERATE)
        session.missing_context_fields = []
    else:
        # Might already be in NEEDS_CLARIFICATION, transition_ticket allows self-transitions for this state
        session.status = transition_ticket(session.status, TicketStatus.NEEDS_CLARIFICATION)
        session.missing_context_fields = missing_fields
        if next_questions:
            session.history.append(Message(role="assistant", content=" ".join(next_questions)))
            
    repo.save(session)
    return _create_agentic_response(session, "clarification_processed", next_questions)


def process_generate(ticket_id: str, repo: TicketRepository) -> AgenticResponse:
    """Generates the actual ticket metadata based on complete history."""
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")
        
    # Validation
    if session.status != TicketStatus.READY_TO_GENERATE:
        # Idempotency check: if it's already generated, just return it.
        if session.status == TicketStatus.GENERATED and session.ticket_data is not None:
            data = GenerateResponseData(ticket=session.ticket_data, version=session.ticket_version)
            return _create_agentic_response(session, "ticket_already_generated", data=data)
        
        raise InvalidStateException(f"Cannot generate ticket from {session.status.value} state")

    prompt = _build_v1_history_prompt(session)
    client = get_ai_client()
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": GENERATION_PROMPT},
                {"role": "user", "content": f"Historial de conversación:\n{prompt}"},
            ],
            model=settings.AI_MODEL_NAME,
            temperature=0.2, # slightly higher for creative writing
            response_format={"type": "json_object"},
        )
        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValueError("Empty response from AI generation")
            
        ticket_json = json.loads(raw_content)
        ticket_data = TicketMetadata(**ticket_json)
        
    except Exception as e:
        logger.exception("Error generating ticket")
        raise AIServiceError("Failed to generate ticket metadata") from e

    # Update state
    session.status = transition_ticket(session.status, TicketStatus.GENERATED)
    session.ticket_data = ticket_data
    session.ticket_version += 1
    session.missing_context_fields = []
    
    repo.save(session)
    
    data = GenerateResponseData(ticket=session.ticket_data, version=session.ticket_version)
    return _create_agentic_response(session, "ticket_generated", data=data)


def process_revise(ticket_id: str, feedback: str, repo: TicketRepository) -> AgenticResponse:
    """Revises an existing ticket based on feedback."""
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")
        
    if session.status != TicketStatus.GENERATED:
        raise InvalidStateException(f"Cannot revise ticket from {session.status.value} state")
        
    # Transition to REVISING temporarily
    session.status = transition_ticket(session.status, TicketStatus.REVISING)
    
    if not session.ticket_data:
        raise AIServiceError("Cannot revise a ticket without generated data")
    
    client = get_ai_client()
    user_prompt = f"Ticket actual:\n{session.ticket_data.model_dump_json()}\n\nFeedback del usuario:\n{feedback}"
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": REVISION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            model=settings.AI_MODEL_NAME,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValueError("Empty response from AI revision")
            
        revised_json = json.loads(raw_content)
        revised_ticket_data = TicketMetadata(**revised_json["ticket"])
        diff_summary = revised_json.get("diff_summary", "")
        
    except Exception as e:
        logger.exception("Error revising ticket")
        # Rollback state transition
        session.status = transition_ticket(session.status, TicketStatus.GENERATED) 
        repo.save(session)
        raise AIServiceError("Failed to revise ticket metadata") from e

    # Add to history so LLM has context of the revision
    session.history.append(Message(role="user", content=f"Revisión solicitada: {feedback}"))
    session.history.append(Message(role="assistant", content=f"Ticket revisado. {diff_summary}"))

    # Update state back to GENERATED
    session.status = transition_ticket(session.status, TicketStatus.GENERATED)
    session.ticket_data = revised_ticket_data
    session.ticket_version += 1
    
    repo.save(session)
    
    data = ReviseResponseData(
        ticket=session.ticket_data, 
        version=session.ticket_version,
        diff_summary=diff_summary
    )
    return _create_agentic_response(session, "ticket_revised", data=data)


def process_finalize(ticket_id: str, repo: TicketRepository) -> AgenticResponse:
    """Finalizes the ticket, locking it from further changes."""
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")
        
    if session.status == TicketStatus.FINALIZED:
        # Idempotency
        return _create_agentic_response(session, "ticket_already_finalized")
        
    if session.status != TicketStatus.GENERATED:
        raise InvalidStateException(f"Cannot finalize ticket from {session.status.value} state")
        
    session.status = transition_ticket(session.status, TicketStatus.FINALIZED)
    repo.save(session)
    
    return _create_agentic_response(session, "ticket_finalized")
