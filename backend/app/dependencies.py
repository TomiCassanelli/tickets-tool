from .repository import InMemoryTicketRepository

# Global in-memory repository instance for Phase 2
_ticket_repository = InMemoryTicketRepository()

def get_ticket_repository() -> InMemoryTicketRepository:
    return _ticket_repository
