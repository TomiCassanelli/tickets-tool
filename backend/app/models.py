from pydantic import BaseModel, Field
from typing import List
from typing import Optional


class TicketMetadata(BaseModel):
    titulo: str = Field(..., description="Short and clear title for the issue or feature")
    tipo: str = Field(..., description="Must be 'Bug', 'Feature' or 'Task'")
    prioridad: str = Field(..., description="Must be 'High', 'Medium' or 'Low'")
    contexto: str = Field(default="", description="Technical context or detailed description")
    criterios_de_aceptacion: List[str] = Field(default_factory=list, description="List of acceptance criteria")
    historia_como: str = Field(default="", description="User story 'Como' (who/role)")
    historia_quiero: str = Field(default="", description="User story 'Quiero' (want/goal)")
    historia_para: str = Field(default="", description="User story 'Para' (benefit)")


class TicketResponse(BaseModel):
    metadata: TicketMetadata
    markdown: str
    needs_more_clarification: bool = Field(default=False, description="Whether more clarification is needed")


class ClarifyResponse(BaseModel):
    clarifying_question: str = Field(..., description="Single clarifying question to ask the user")
    needs_more_clarification: bool = Field(default=True, description="Whether more clarification will be needed after answering")
    conversation_context: str = Field(default="", description="Context of what has been clarified so far")


class ClarificationSubmission(BaseModel):
    raw_text: str
    answers: List[str]


class ConversationTurn(BaseModel):
    question: str
    answer: str


class ClarificationRequest(BaseModel):
    raw_text: str
    conversation_history: List[ConversationTurn] = Field(default_factory=list)


class UserRequest(BaseModel):
    raw_text: str
