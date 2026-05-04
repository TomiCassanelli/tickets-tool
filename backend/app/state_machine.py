from enum import Enum

class TicketStatus(str, Enum):
    DRAFT = "DRAFT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY_TO_GENERATE = "READY_TO_GENERATE"
    GENERATED = "GENERATED"
    REVISING = "REVISING"
    FINALIZED = "FINALIZED"

class InvalidStateException(Exception):
    """Raised when an invalid state transition is attempted."""
    pass

# Define valid target states for each current state
VALID_TRANSITIONS = {
    TicketStatus.DRAFT: [TicketStatus.NEEDS_CLARIFICATION, TicketStatus.READY_TO_GENERATE],
    TicketStatus.NEEDS_CLARIFICATION: [TicketStatus.NEEDS_CLARIFICATION, TicketStatus.READY_TO_GENERATE],
    TicketStatus.READY_TO_GENERATE: [TicketStatus.GENERATED],
    TicketStatus.GENERATED: [TicketStatus.REVISING, TicketStatus.FINALIZED],
    TicketStatus.REVISING: [TicketStatus.GENERATED],
    TicketStatus.FINALIZED: []  # Terminal state
}

def transition_ticket(current_status: TicketStatus, new_status: TicketStatus) -> TicketStatus:
    """
    Attempts to transition from current_status to new_status.
    Returns the new_status if valid, raises InvalidStateException otherwise.
    """
    if new_status not in VALID_TRANSITIONS.get(current_status, []):
        raise InvalidStateException(
            f"Cannot transition from {current_status.value} to {new_status.value}"
        )
    return new_status
