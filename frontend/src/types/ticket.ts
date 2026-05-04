export const TICKET_STATUS = {
  NEEDS_CLARIFICATION: "NEEDS_CLARIFICATION",
  READY_TO_GENERATE: "READY_TO_GENERATE",
  GENERATED: "GENERATED",
  FINALIZED: "FINALIZED",
} as const;

export type TicketStatus = (typeof TICKET_STATUS)[keyof typeof TICKET_STATUS];

export interface TicketMetadata {
  titulo: string;
  tipo: string;
  prioridad: string;
  contexto: string;
  criterios_de_aceptacion: string[];
  historia_como: string;
  historia_quiero: string;
  historia_para: string;
  alcance?: string;
  riesgos: string[];
  definition_of_done: string[];
  notas_tecnicas?: string;
}

export interface CreateTicketResponseData {
  ticket: TicketMetadata;
  version: number;
}

export interface UpdateTicketResponseData {
  ticket: TicketMetadata;
  version: number;
  diff_summary: string;
}

export interface ToolCallingMeta {
  schema_version: string;
  ticket_id: string;
  status: string;
  action: string;
  next_allowed_actions: string[];
  missing_context_fields: string[];
  next_questions: string[];
  intent: string;
  objective: string;
}

export interface AgenticResponse<T> {
  meta: ToolCallingMeta;
  data: T | null;
}

export interface ConversationTurn {
  question: string;
  answer: string;
}
