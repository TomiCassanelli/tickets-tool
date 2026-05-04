from typing import Optional, Dict
from threading import Lock
from .models import TicketSession

class TicketRepository:
    def save(self, session: TicketSession) -> TicketSession:
        raise NotImplementedError

    def get(self, session_id: str) -> Optional[TicketSession]:
        raise NotImplementedError

class InMemoryTicketRepository(TicketRepository):
    """
    Thread-safe in-memory repository for storing TicketSessions.
    Used for Phase 1 as a placeholder for a real database.
    """
    def __init__(self):
        self._storage: Dict[str, TicketSession] = {}
        self._lock = Lock()

    def save(self, session: TicketSession) -> TicketSession:
        with self._lock:
            # Pydantic models can be copied to avoid reference mutation bugs
            self._storage[session.id] = session.model_copy(deep=True)
            return self._storage[session.id]

    def get(self, session_id: str) -> Optional[TicketSession]:
        with self._lock:
            session = self._storage.get(session_id)
            if session:
                return session.model_copy(deep=True)
            return None
