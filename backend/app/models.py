from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Generic, TypeVar, Literal
import uuid
from datetime import datetime
from .state_machine import TicketStatus


class TicketMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    titulo: str = Field(..., description="Short and clear title for the issue or feature")
    tipo: str = Field(..., description="Must be 'Bug', 'Feature' or 'Task'")
    prioridad: str = Field(..., description="Must be 'High', 'Medium' or 'Low'")
    contexto: str = Field(default="", description="Technical context or detailed description")
    criterios_de_aceptacion: List[str] = Field(default_factory=list, description="List of acceptance criteria")
    historia_como: str = Field(default="", description="User story 'Como' (who/role)")
    historia_quiero: str = Field(default="", description="User story 'Quiero' (want/goal)")
    historia_para: str = Field(default="", description="User story 'Para' (benefit)")
    
    # Nuevos campos fase 1
    alcance: Optional[str] = Field(default="", description="Scope of the ticket")
    riesgos: List[str] = Field(default_factory=list, description="Potential risks")
    definition_of_done: List[str] = Field(default_factory=list, description="Definition of Done (DoD)")
    notas_tecnicas: Optional[str] = Field(default="", description="Technical notes")


class UserPreferences(BaseModel):
    model_config = ConfigDict(extra="ignore")

    language: str = Field(default="es", description="Preferred language code")
    tone: str = Field(default="profesional", description="Preferred response tone")
    technical_level: str = Field(default="intermedio", description="Technical depth preference")
    response_length: str = Field(default="media", description="Expected response length")


class ContextPack(BaseModel):
    model_config = ConfigDict(extra="ignore")

    objective: str = Field(default="", description="Primary user objective")
    constraints: List[str] = Field(default_factory=list, description="Explicit constraints mentioned by user")
    recent_turns: List[str] = Field(default_factory=list, description="Condensed recent chat turns")
    preferences: UserPreferences = Field(default_factory=UserPreferences)


IntentType = Literal["qa", "redaccion", "resumen", "analisis", "accionable", "codigo", "soporte"]


class AnalysisAIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    is_ready: bool = False
    missing_context_fields: List[str] = Field(default_factory=list)
    next_questions: List[str] = Field(default_factory=list)
    intent: IntentType = "soporte"
    objective: str = Field(default="")
    constraints: List[str] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class RevisionAIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket: TicketMetadata
    diff_summary: str = Field(default="", description="Summary of applied changes")


class QualityReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    passed: bool
    score: int = Field(default=0, ge=0, le=100)
    issues: List[str] = Field(default_factory=list)


class TicketResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    metadata: TicketMetadata
    markdown: str
    needs_more_clarification: bool = Field(default=False, description="Whether more clarification is needed")


class ClarifyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    clarifying_question: str = Field(..., description="Single clarifying question to ask the user")
    needs_more_clarification: bool = Field(default=True, description="Whether more clarification will be needed after answering")
    conversation_context: str = Field(default="", description="Context of what has been clarified so far")


class ConversationTurn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question: str
    answer: str


class AnswerQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    answer: str


class UserRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    raw_text: str


# Nuevos modelos base Fase 1/2 para el flujo conversacional y persistencia
class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TicketSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TicketStatus = Field(default=TicketStatus.DRAFT)
    history: List[Message] = Field(default_factory=list)
    ticket_data: Optional[TicketMetadata] = None
    ticket_version: int = Field(default=0)
    missing_context_fields: List[str] = Field(default_factory=list)
    intent: IntentType = "soporte"
    objective: str = Field(default="")
    constraints: List[str] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# API V1 Models (Tool-calling readiness)
class ToolCallingMeta(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    schema_version: str = "1.0"
    ticket_id: str
    status: TicketStatus
    action: str
    next_allowed_actions: List[str]
    missing_context_fields: List[str] = Field(default_factory=list)
    next_questions: List[str] = Field(default_factory=list)
    intent: IntentType = "soporte"
    objective: str = Field(default="")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    quality_score: int = Field(default=0, ge=0, le=100)
    retries_used: int = Field(default=0, ge=0)


T = TypeVar('T')

class AgenticResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="ignore")
    
    meta: ToolCallingMeta
    data: Optional[T] = None


class StartTicketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    prompt: str


class CreateTicketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # Empty request for now, but good practice to have a model

class UpdateTicketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    feedback: str = Field(..., description="Instructions on what to change in the ticket")

class FinishTicketRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    # Empty request

class CreateTicketResponseData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ticket: TicketMetadata
    version: int

class UpdateTicketResponseData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ticket: TicketMetadata
    version: int
    diff_summary: str = Field(default="", description="Summary of changes made based on feedback")
