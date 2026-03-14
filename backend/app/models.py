from pydantic import BaseModel, Field
from typing import List


class TicketMetadata(BaseModel):
    titulo: str = Field(..., description="Short and clear title for the issue or feature")
    tipo: str = Field(..., description="Must be 'Bug', 'Feature' or 'Task'")
    prioridad: str = Field(..., description="Must be 'High', 'Medium' or 'Low'")
    contexto: str = Field(..., description="Technical context or detailed description")
    criterios_de_aceptacion: List[str] = Field(..., description="List of acceptance criteria")


class TicketResponse(BaseModel):
    metadata: TicketMetadata
    markdown: str


class UserRequest(BaseModel):
    raw_text: str
