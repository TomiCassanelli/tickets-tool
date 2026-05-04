from __future__ import annotations

from typing import List

from ..models import QualityReport, TicketMetadata


def score_analysis_quality(
    *,
    is_ready: bool,
    missing_context_fields: List[str],
    next_questions: List[str],
    objective: str,
) -> QualityReport:
    issues: List[str] = []
    score = 100

    if not objective.strip():
        issues.append("Objective is missing")
        score -= 25

    if is_ready and missing_context_fields:
        issues.append("Ready response still has missing context fields")
        score -= 20

    if not is_ready and not next_questions:
        issues.append("Clarification flow requires at least one question")
        score -= 25

    if not is_ready and len(next_questions) > 1:
        issues.append("Clarification flow should ask exactly one question")
        score -= 35

    return QualityReport(passed=score >= 70, score=max(score, 0), issues=issues)


def score_ticket_quality(ticket: TicketMetadata) -> QualityReport:
    issues: List[str] = []
    score = 100

    if len(ticket.titulo.strip()) < 8:
        issues.append("Title is too short")
        score -= 15

    if len(ticket.contexto.strip()) < 40:
        issues.append("Context should be more specific")
        score -= 20

    if len(ticket.criterios_de_aceptacion) < 2:
        issues.append("At least two acceptance criteria are required")
        score -= 20

    if ticket.tipo not in {"Bug", "Feature", "Task"}:
        issues.append("Ticket type is invalid")
        score -= 20

    if ticket.prioridad not in {"High", "Medium", "Low"}:
        issues.append("Ticket priority is invalid")
        score -= 20

    if len(ticket.definition_of_done) < 2:
        issues.append("Definition of done should include at least two items")
        score -= 10

    return QualityReport(passed=score >= 70, score=max(score, 0), issues=issues)
