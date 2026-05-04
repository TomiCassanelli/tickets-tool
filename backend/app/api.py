import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from .models import (
    StartTicketRequest, AnswerQuestionRequest, UpdateTicketRequest,
    AgenticResponse, CreateTicketResponseData, UpdateTicketResponseData
)
from .dependencies import get_ticket_repository
from .repository import TicketRepository
from .services.ticket_service import (
    start_ticket_flow, answer_ticket_question, create_ticket,
    update_ticket, finish_ticket
)
from .services.exceptions import AIServiceError
from .state_machine import InvalidStateException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("/start", response_model=AgenticResponse[Any])
async def start_ticket(
    req: StartTicketRequest,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return start_ticket_flow(req.prompt, repo)
    except AIServiceError as e:
        logger.error(f"AI service error while starting ticket: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error while starting ticket")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/answer", response_model=AgenticResponse[Any])
async def answer_question(
    ticket_id: str,
    req: AnswerQuestionRequest,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return answer_ticket_question(ticket_id, req.answer, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error while answering question: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error while answering question")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/create", response_model=AgenticResponse[CreateTicketResponseData])
async def create_ticket_endpoint(
    ticket_id: str,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return create_ticket(ticket_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error while creating ticket: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error while creating ticket")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/update", response_model=AgenticResponse[UpdateTicketResponseData])
async def update_ticket_endpoint(
    ticket_id: str,
    req: UpdateTicketRequest,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return update_ticket(ticket_id, req.feedback, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error while updating ticket: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error while updating ticket")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/finish", response_model=AgenticResponse[Any])
async def finish_ticket_endpoint(
    ticket_id: str,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return finish_ticket(ticket_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error while finishing ticket")
        raise HTTPException(status_code=500, detail="Internal server error")
