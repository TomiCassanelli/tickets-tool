import type {
  AgenticResponse,
  CreateTicketResponseData,
  UpdateTicketResponseData,
} from "../types/ticket";

interface ApiErrorPayload {
  detail?: string;
}

const JSON_HEADERS = { "Content-Type": "application/json" };

async function parseJson<T>(response: Response): Promise<T> {
  return (await response.json().catch(() => ({}))) as T;
}

async function request<T>(url: string, init: RequestInit): Promise<AgenticResponse<T>> {
  const response = await fetch(url, init);
  if (!response.ok) {
    const payload = await parseJson<ApiErrorPayload>(response);
    throw new Error(payload.detail || `HTTP ${response.status}`);
  }

  return (await parseJson<unknown>(response)) as AgenticResponse<T>;
}

export async function startTicket(apiBase: string, prompt: string): Promise<AgenticResponse<null>> {
  return request<null>(`${apiBase}/api/tickets/start`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ prompt }),
  });
}

export async function answerTicket(
  apiBase: string,
  ticketId: string,
  answer: string,
): Promise<AgenticResponse<null>> {
  return request<null>(`${apiBase}/api/tickets/${ticketId}/answer`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ answer }),
  });
}

export async function createTicket(
  apiBase: string,
  ticketId: string,
): Promise<AgenticResponse<CreateTicketResponseData>> {
  return request<CreateTicketResponseData>(`${apiBase}/api/tickets/${ticketId}/create`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
}

export async function updateTicket(
  apiBase: string,
  ticketId: string,
  feedback: string,
): Promise<AgenticResponse<UpdateTicketResponseData>> {
  return request<UpdateTicketResponseData>(`${apiBase}/api/tickets/${ticketId}/update`, {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify({ feedback }),
  });
}

export async function finishTicket(apiBase: string, ticketId: string): Promise<AgenticResponse<null>> {
  return request<null>(`${apiBase}/api/tickets/${ticketId}/finish`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
}
