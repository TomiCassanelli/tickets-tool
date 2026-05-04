import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ..core.ai_client import get_ai_client
from ..core.config import settings
from ..models import (
    AgenticResponse,
    AnalysisAIResponse,
    ContextPack,
    CreateTicketResponseData,
    Message,
    RevisionAIResponse,
    TicketMetadata,
    TicketSession,
    ToolCallingMeta,
    UpdateTicketResponseData,
)
from ..prompts import ANALYSIS_PROMPT, GENERATION_PROMPT, REVISION_PROMPT
from ..repository import TicketRepository
from ..state_machine import InvalidStateException, TicketStatus, transition_ticket
from .exceptions import AIServiceError
from .quality_service import score_analysis_quality, score_ticket_quality

logger = logging.getLogger(__name__)

MAX_AI_RETRIES = 2
RETRY_SUFFIX = "\n\nTu salida previa no cumplio el formato o calidad. Corrige y responde SOLO JSON valido."


def _build_v1_history_prompt(session: TicketSession) -> str:
    prompt = ""
    for msg in session.history:
        if msg.role == "user":
            prompt += f"Usuario: {msg.content}\n"
        elif msg.role == "assistant":
            prompt += f"Asistente: {msg.content}\n"
    return prompt


def _compact_constraints(session: TicketSession) -> List[str]:
    compacted: List[str] = []
    for constraint in session.constraints:
        clean = constraint.strip()
        if clean and clean not in compacted:
            compacted.append(clean)
        if len(compacted) >= 5:
            break
    return compacted


def _build_context_pack(session: TicketSession) -> ContextPack:
    turns = [f"{msg.role}: {msg.content.strip()}" for msg in session.history if msg.content.strip()]
    recent_turns = turns[-5:]

    objective = session.objective.strip()
    if not objective:
        user_turns = [msg.content.strip() for msg in session.history if msg.role == "user" and msg.content.strip()]
        objective = user_turns[-1] if user_turns else ""

    return ContextPack(
        objective=objective,
        constraints=_compact_constraints(session),
        recent_turns=recent_turns,
        preferences=session.preferences,
    )


def _call_ai_json(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.0,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    client = get_ai_client()
    selected_model = model_name or settings.AI_MODEL_NAME
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=selected_model,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        logger.exception("AI provider request failed")
        raise AIServiceError("Error communicating with AI provider") from exc

    try:
        raw_content = response.choices[0].message.content
        if not raw_content:
            raise ValueError("Empty response")
        return json.loads(raw_content)
    except Exception as exc:
        logger.exception("AI provider returned invalid JSON")
        raise AIServiceError("Invalid response structure from AI") from exc


def _normalize_analysis_output(parsed: AnalysisAIResponse) -> AnalysisAIResponse:
    if not parsed.is_ready:
        parsed.next_questions = parsed.next_questions[:1]
    else:
        parsed.next_questions = []
        parsed.missing_context_fields = []
    parsed.constraints = [item.strip() for item in parsed.constraints if item.strip()][:5]
    parsed.objective = parsed.objective.strip()
    return parsed


def _call_analysis_ai(session: TicketSession) -> AnalysisAIResponse:
    prompt = _build_v1_history_prompt(session)
    context_pack = _build_context_pack(session)
    base_user_message = (
        f"Historial de conversacion:\n{prompt}\n"
        f"Context pack:\n{context_pack.model_dump_json()}"
    )

    last_error = ""
    retries_used = 0
    fallback_used = False
    for attempt in range(MAX_AI_RETRIES + 1):
        retry_instruction = RETRY_SUFFIX if attempt > 0 else ""
        model_name = settings.AI_MODEL_NAME

        raw_data = _call_ai_json(
            [
                {"role": "system", "content": ANALYSIS_PROMPT},
                {"role": "user", "content": base_user_message + retry_instruction},
            ],
            temperature=0.0,
            model_name=model_name,
        )

        try:
            parsed = AnalysisAIResponse.model_validate(raw_data)
            parsed = _normalize_analysis_output(parsed)
        except ValidationError as exc:
            logger.warning("Analysis output schema validation failed on attempt %s", attempt + 1)
            retries_used = attempt + 1
            last_error = str(exc)
            continue

        quality = score_analysis_quality(
            is_ready=parsed.is_ready,
            missing_context_fields=parsed.missing_context_fields,
            next_questions=parsed.next_questions,
            objective=parsed.objective,
        )
        if quality.passed:
            return parsed

        logger.warning("Analysis quality check failed on attempt %s: %s", attempt + 1, quality.issues)
        retries_used = attempt + 1
        last_error = ", ".join(quality.issues)

    raise AIServiceError(f"Analysis quality failed after retries: {last_error}")


def _create_agentic_response(
    session: TicketSession,
    action: str,
    *,
    next_questions: Optional[List[str]] = None,
    data: Any = None,
    confidence: float = 0.5,
    quality_score: int = 0,
    retries_used: int = 0,
) -> AgenticResponse:
    if next_questions is None:
        next_questions = []

    next_actions: List[str] = []
    if session.status == TicketStatus.NEEDS_CLARIFICATION:
        next_actions = [f"/api/tickets/{session.id}/answer"]
    elif session.status == TicketStatus.READY_TO_GENERATE:
        next_actions = [f"/api/tickets/{session.id}/create"]
    elif session.status == TicketStatus.GENERATED:
        next_actions = [f"/api/tickets/{session.id}/update", f"/api/tickets/{session.id}/finish"]

    meta = ToolCallingMeta(
        ticket_id=session.id,
        status=session.status,
        action=action,
        next_allowed_actions=next_actions,
        missing_context_fields=session.missing_context_fields,
        next_questions=next_questions,
        intent=session.intent,
        objective=session.objective,
        confidence=confidence,
        quality_score=quality_score,
        retries_used=retries_used,
    )
    return AgenticResponse(meta=meta, data=data)


def start_ticket_flow(prompt: str, repo: TicketRepository) -> AgenticResponse:
    session = TicketSession()
    session.history.append(Message(role="user", content=prompt))

    analysis_result = _call_analysis_ai(session)
    quality = score_analysis_quality(
        is_ready=analysis_result.is_ready,
        missing_context_fields=analysis_result.missing_context_fields,
        next_questions=analysis_result.next_questions,
        objective=analysis_result.objective,
    )

    session.intent = analysis_result.intent
    session.objective = analysis_result.objective
    session.constraints = analysis_result.constraints
    session.preferences = analysis_result.preferences

    if analysis_result.is_ready:
        session.status = transition_ticket(session.status, TicketStatus.READY_TO_GENERATE)
        session.missing_context_fields = []
    else:
        session.status = transition_ticket(session.status, TicketStatus.NEEDS_CLARIFICATION)
        session.missing_context_fields = analysis_result.missing_context_fields
        if analysis_result.next_questions:
            session.history.append(Message(role="assistant", content=analysis_result.next_questions[0]))

    repo.save(session)
    return _create_agentic_response(
        session,
        "started",
        next_questions=analysis_result.next_questions,
        confidence=analysis_result.confidence,
        quality_score=quality.score,
    )


def answer_ticket_question(ticket_id: str, answer: str, repo: TicketRepository) -> AgenticResponse:
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")

    if session.status not in [TicketStatus.NEEDS_CLARIFICATION, TicketStatus.READY_TO_GENERATE]:
        raise InvalidStateException(f"Cannot clarify a ticket in {session.status.value} state")

    session.history.append(Message(role="user", content=answer))
    analysis_result = _call_analysis_ai(session)
    quality = score_analysis_quality(
        is_ready=analysis_result.is_ready,
        missing_context_fields=analysis_result.missing_context_fields,
        next_questions=analysis_result.next_questions,
        objective=analysis_result.objective,
    )

    session.intent = analysis_result.intent
    session.objective = analysis_result.objective
    session.constraints = analysis_result.constraints
    session.preferences = analysis_result.preferences

    if analysis_result.is_ready:
        session.status = transition_ticket(session.status, TicketStatus.READY_TO_GENERATE)
        session.missing_context_fields = []
    else:
        session.status = transition_ticket(session.status, TicketStatus.NEEDS_CLARIFICATION)
        session.missing_context_fields = analysis_result.missing_context_fields
        if analysis_result.next_questions:
            session.history.append(Message(role="assistant", content=analysis_result.next_questions[0]))

    repo.save(session)
    return _create_agentic_response(
        session,
        "answer_saved",
        next_questions=analysis_result.next_questions,
        confidence=analysis_result.confidence,
        quality_score=quality.score,
    )


def _generate_ticket_once(session: TicketSession, retry_instruction: str = "", model_name: Optional[str] = None) -> TicketMetadata:
    prompt = _build_v1_history_prompt(session)
    context_pack = _build_context_pack(session)
    user_message = (
        f"Historial de conversacion:\n{prompt}\n"
        f"Context pack:\n{context_pack.model_dump_json()}"
        f"{retry_instruction}"
    )
    raw_data = _call_ai_json(
        [
            {"role": "system", "content": GENERATION_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        model_name=model_name,
    )
    return TicketMetadata.model_validate(raw_data)


def create_ticket(ticket_id: str, repo: TicketRepository) -> AgenticResponse:
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")

    if session.status != TicketStatus.READY_TO_GENERATE:
        if session.status == TicketStatus.GENERATED and session.ticket_data is not None:
            current_quality = score_ticket_quality(session.ticket_data)
            data = CreateTicketResponseData(ticket=session.ticket_data, version=session.ticket_version)
            return _create_agentic_response(session, "already_created", data=data, quality_score=current_quality.score)
        raise InvalidStateException(f"Cannot generate ticket from {session.status.value} state")

    last_error = ""
    retries_used = 0
    ticket_data: Optional[TicketMetadata] = None
    quality_score = 0

    for attempt in range(MAX_AI_RETRIES + 1):
        retry_instruction = RETRY_SUFFIX if attempt > 0 else ""
        model_name = settings.AI_MODEL_NAME

        try:
            candidate = _generate_ticket_once(session, retry_instruction=retry_instruction, model_name=model_name)
        except (AIServiceError, ValidationError) as exc:
            logger.warning("Ticket generation attempt %s failed", attempt + 1)
            retries_used = attempt + 1
            last_error = str(exc)
            continue

        quality = score_ticket_quality(candidate)
        quality_score = quality.score
        if quality.passed:
            ticket_data = candidate
            retries_used = attempt
            break

        retries_used = attempt + 1
        last_error = ", ".join(quality.issues)
        logger.warning("Ticket quality failed on attempt %s: %s", attempt + 1, quality.issues)

    if ticket_data is None:
        raise AIServiceError(f"Failed to generate high-quality ticket: {last_error}")

    session.status = transition_ticket(session.status, TicketStatus.GENERATED)
    session.ticket_data = ticket_data
    session.ticket_version += 1
    session.missing_context_fields = []
    repo.save(session)

    data = CreateTicketResponseData(ticket=session.ticket_data, version=session.ticket_version)
    return _create_agentic_response(
        session,
        "created",
        data=data,
        confidence=0.8,
        quality_score=quality_score,
        retries_used=retries_used,
    )


def update_ticket(ticket_id: str, feedback: str, repo: TicketRepository) -> AgenticResponse:
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")

    if session.status != TicketStatus.GENERATED:
        raise InvalidStateException(f"Cannot revise ticket from {session.status.value} state")

    session.status = transition_ticket(session.status, TicketStatus.REVISING)

    if not session.ticket_data:
        raise AIServiceError("Cannot revise a ticket without generated data")

    user_prompt = f"Ticket actual:\n{session.ticket_data.model_dump_json()}\n\nFeedback del usuario:\n{feedback}"

    try:
        raw_data = _call_ai_json(
            [
                {"role": "system", "content": REVISION_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        revised_data = RevisionAIResponse.model_validate(raw_data)
        revised_ticket_data = revised_data.ticket
        diff_summary = revised_data.diff_summary
    except Exception as exc:
        logger.exception("Error revising ticket")
        session.status = transition_ticket(session.status, TicketStatus.GENERATED)
        repo.save(session)
        raise AIServiceError("Failed to revise ticket metadata") from exc

    quality = score_ticket_quality(revised_ticket_data)
    if not quality.passed:
        session.status = transition_ticket(session.status, TicketStatus.GENERATED)
        repo.save(session)
        raise AIServiceError(f"Revision did not pass quality checks: {', '.join(quality.issues)}")

    session.history.append(Message(role="user", content=f"Revision solicitada: {feedback}"))
    session.history.append(Message(role="assistant", content=f"Ticket revisado. {diff_summary}"))
    session.status = transition_ticket(session.status, TicketStatus.GENERATED)
    session.ticket_data = revised_ticket_data
    session.ticket_version += 1
    repo.save(session)

    data = UpdateTicketResponseData(ticket=session.ticket_data, version=session.ticket_version, diff_summary=diff_summary)
    return _create_agentic_response(
        session,
        "updated",
        data=data,
        confidence=0.75,
        quality_score=quality.score,
    )


def finish_ticket(ticket_id: str, repo: TicketRepository) -> AgenticResponse:
    session = repo.get(ticket_id)
    if not session:
        raise ValueError(f"Ticket session {ticket_id} not found")

    if session.status == TicketStatus.FINALIZED:
        final_quality = score_ticket_quality(session.ticket_data) if session.ticket_data else None
        quality_score = final_quality.score if final_quality else 0
        return _create_agentic_response(session, "already_finished", quality_score=quality_score)

    if session.status != TicketStatus.GENERATED:
        raise InvalidStateException(f"Cannot finalize ticket from {session.status.value} state")

    quality = score_ticket_quality(session.ticket_data) if session.ticket_data else None
    if quality and not quality.passed:
        raise AIServiceError(f"Cannot finalize low-quality ticket: {', '.join(quality.issues)}")

    session.status = transition_ticket(session.status, TicketStatus.FINALIZED)
    repo.save(session)
    return _create_agentic_response(session, "finished", quality_score=quality.score if quality else 0)
