import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from .models import (
    IntakeRequest, ClarificationRequest, ReviseRequest, 
    AgenticResponse, GenerateResponseData, ReviseResponseData
)
from .dependencies import get_ticket_repository
from .repository import TicketRepository
from .services.ticket_service import (
    process_intake, process_clarification, process_generate, 
    process_revise, process_finalize
)
from .services.exceptions import AIServiceError
from .state_machine import InvalidStateException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("/intake", response_model=AgenticResponse[Any])
async def intake_ticket(
    req: IntakeRequest, 
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return process_intake(req.prompt, repo)
    except AIServiceError as e:
        logger.error(f"AI service error during intake: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error in intake")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/clarifications", response_model=AgenticResponse[Any])
async def clarify_ticket(
    ticket_id: str,
    req: ClarificationRequest,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return process_clarification(ticket_id, req.answer, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error during clarification: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error in clarification")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/generate", response_model=AgenticResponse[GenerateResponseData])
async def generate_ticket(
    ticket_id: str,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return process_generate(ticket_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error during generation: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error in generation")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/revise", response_model=AgenticResponse[ReviseResponseData])
async def revise_ticket(
    ticket_id: str,
    req: ReviseRequest,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return process_revise(ticket_id, req.feedback, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIServiceError as e:
        logger.error(f"AI service error during revision: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service")
    except Exception:
        logger.exception("Unexpected error in revision")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{ticket_id}/finalize", response_model=AgenticResponse[Any])
async def finalize_ticket(
    ticket_id: str,
    repo: TicketRepository = Depends(get_ticket_repository)
):
    try:
        return process_finalize(ticket_id, repo)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Unexpected error in finalize")
        raise HTTPException(status_code=500, detail="Internal server error")
