"use client";

import { KeyboardEvent, useState } from "react";
import ReactMarkdown from "react-markdown";

import {
  answerTicket,
  createTicket,
  finishTicket,
  startTicket,
  updateTicket,
} from "../lib/ticketApi";
import { buildTicketMarkdown } from "../lib/ticketMarkdown";
import { TICKET_STATUS, type ConversationTurn, type ToolCallingMeta } from "../types/ticket";

const API_BASE_DEFAULT = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

interface QuickAction {
  id: "create" | "finish" | "update";
  label: string;
}

function TicketModal({
  markdown,
  onClose,
}: {
  markdown: string;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4">
      <div className="max-h-[88vh] w-full max-w-2xl overflow-auto rounded-3xl border border-slate-200 bg-white shadow-2xl">
        <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-3">
          <p className="text-sm font-semibold text-slate-800">Ticket listo para copiar</p>
          <button
            onClick={onClose}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
          >
            Cerrar
          </button>
        </div>
        <article className="prose prose-sm max-w-none px-5 py-4">
          <ReactMarkdown>{markdown}</ReactMarkdown>
        </article>
      </div>
    </div>
  );
}

function AssistantBubble({
  text,
  quickActions,
  onQuickAction,
}: {
  text: string;
  quickActions: QuickAction[];
  onQuickAction: (actionId: QuickAction["id"]) => void;
}) {
  return (
    <div className="flex gap-3">
      <div className="mt-1 h-8 w-8 shrink-0 rounded-full bg-indigo-600 text-center text-xs font-semibold leading-8 text-white">
        AI
      </div>
      <div className="max-w-[88%] rounded-2xl rounded-tl-sm border border-indigo-100 bg-white px-4 py-3 shadow-sm">
        <p className="text-sm leading-6 text-slate-700">{text}</p>
        {quickActions.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={() => onQuickAction(action.id)}
                className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
              >
                {action.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-slate-100 px-4 py-3 text-sm leading-6 text-slate-800 shadow-sm">
        {text}
      </div>
    </div>
  );
}

export default function HomePage() {
  const [apiBase, setApiBase] = useState(API_BASE_DEFAULT);
  const [ticketId, setTicketId] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [meta, setMeta] = useState<ToolCallingMeta | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "Hola. Contame que ticket necesitas y te acompano paso a paso.",
    },
  ]);
  const [conversationTurns, setConversationTurns] = useState<ConversationTurn[]>([]);
  const [lastQuestion, setLastQuestion] = useState("");
  const [ticketMarkdown, setTicketMarkdown] = useState("");
  const [pendingUpdate, setPendingUpdate] = useState(false);
  const [updateFeedback, setUpdateFeedback] = useState("");

  const canAnswer = meta?.status === TICKET_STATUS.NEEDS_CLARIFICATION;
  const canCreate = meta?.status === TICKET_STATUS.READY_TO_GENERATE;
  const canUpdateOrFinish = meta?.status === TICKET_STATUS.GENERATED;

  function appendAssistant(text: string) {
    setMessages((prev) => [...prev, { role: "assistant", text }]);
  }

  function explainStatus(nextMeta: ToolCallingMeta): string {
    if (nextMeta.status === TICKET_STATUS.NEEDS_CLARIFICATION && nextMeta.next_questions[0]) {
      return nextMeta.next_questions[0];
    }
    if (nextMeta.status === TICKET_STATUS.READY_TO_GENERATE) {
      return "Perfecto, ya tengo contexto suficiente. Puedo generar el ticket cuando quieras.";
    }
    if (nextMeta.status === TICKET_STATUS.GENERATED) {
      return "Listo, ticket generado. Queres que lo ajustemos o lo finalizamos?";
    }
    if (nextMeta.status === TICKET_STATUS.FINALIZED) {
      return "Excelente, ticket finalizado. Si queres arrancamos uno nuevo.";
    }
    return "Te sigo leyendo.";
  }

  function quickActionsForMeta(nextMeta: ToolCallingMeta): QuickAction[] {
    if (nextMeta.status === TICKET_STATUS.READY_TO_GENERATE) {
      return [{ id: "create", label: "Generar ticket" }];
    }
    if (nextMeta.status === TICKET_STATUS.GENERATED) {
      return [
        { id: "update", label: "Ajustar ticket" },
        { id: "finish", label: "Finalizar ticket" },
      ];
    }
    return [];
  }

  function syncMeta(nextMeta: ToolCallingMeta) {
    setMeta(nextMeta);
    setTicketId(nextMeta.ticket_id);
    setLastQuestion(nextMeta.next_questions[0] || "");
  }

  async function handleStartFlow(text: string) {
    const response = await startTicket(apiBase, text);
    syncMeta(response.meta);
    appendAssistant(explainStatus(response.meta));
  }

  async function handleClarification(text: string) {
    if (!ticketId) {
      appendAssistant("Necesito un ticket activo para continuar. Empecemos desde el inicio.");
      return;
    }

    const response = await answerTicket(apiBase, ticketId, text);
    syncMeta(response.meta);
    setConversationTurns((prev) => [...prev, { question: lastQuestion, answer: text }]);
    appendAssistant(explainStatus(response.meta));
  }

  async function handleCreateTicket() {
    if (!ticketId) {
      appendAssistant("Necesito ticket_id para generarlo. Empecemos de nuevo.");
      return;
    }

    const response = await createTicket(apiBase, ticketId);
    syncMeta(response.meta);
    if (response.data) {
      setTicketMarkdown(buildTicketMarkdown(response.data.ticket));
    }
    appendAssistant(explainStatus(response.meta));
  }

  async function handleUpdateTicket(feedback: string) {
    if (!ticketId) {
      appendAssistant("No encuentro ticket activo para actualizar.");
      return;
    }

    const response = await updateTicket(apiBase, ticketId, feedback);
    syncMeta(response.meta);
    if (response.data) {
      setTicketMarkdown(buildTicketMarkdown(response.data.ticket));
    }
    appendAssistant("Hecho. Aplique los cambios al ticket.");
    setPendingUpdate(false);
    setUpdateFeedback("");
  }

  async function handleFinishTicket() {
    if (!ticketId) {
      appendAssistant("No hay ticket activo para finalizar.");
      return;
    }

    const response = await finishTicket(apiBase, ticketId);
    syncMeta(response.meta);
    appendAssistant(explainStatus(response.meta));
  }

  async function handlePrimarySend() {
    const text = message.trim();
    if (!text || isLoading) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", text }]);
    setMessage("");
    setIsLoading(true);

    try {
      if (canAnswer) {
        await handleClarification(text);
      } else {
        await handleStartFlow(text);
      }
    } catch (error) {
      appendAssistant(error instanceof Error ? error.message : "Hubo un error inesperado.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleQuickAction(actionId: QuickAction["id"]) {
    if (isLoading) {
      return;
    }

    setIsLoading(true);
    try {
      if (actionId === "create") {
        await handleCreateTicket();
        return;
      }
      if (actionId === "finish") {
        await handleFinishTicket();
        return;
      }
      setPendingUpdate(true);
    } catch (error) {
      appendAssistant(error instanceof Error ? error.message : "No pude ejecutar esa accion.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpdateSubmit() {
    const feedback = updateFeedback.trim();
    if (!feedback || isLoading) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", text: `Ajuste solicitado: ${feedback}` }]);
    setIsLoading(true);
    try {
      await handleUpdateTicket(feedback);
    } catch (error) {
      appendAssistant(error instanceof Error ? error.message : "No pude aplicar el ajuste.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handlePrimarySend();
    }
  }

  function resetChat() {
    setMeta(null);
    setTicketId("");
    setMessages([
      {
        role: "assistant",
        text: "Nuevo chat listo. Contame que ticket queres crear.",
      },
    ]);
    setMessage("");
    setLastQuestion("");
    setTicketMarkdown("");
    setPendingUpdate(false);
    setUpdateFeedback("");
    setConversationTurns([]);
  }

  const quickActions = meta ? quickActionsForMeta(meta) : [];

  return (
    <main className="dot-surface min-h-screen px-3 py-6">
      <div className="mx-auto w-full max-w-md rounded-3xl border border-slate-200 bg-slate-50 shadow-xl">
        <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <button className="rounded-full bg-slate-100 p-2 text-slate-500">☰</button>
          <div className="text-center">
            <p className="text-base font-semibold text-indigo-600">TicketGen AI</p>
            <p className="text-[11px] text-slate-500">Conversacion activa</p>
          </div>
          <button
            onClick={resetChat}
            className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600"
          >
            Reset
          </button>
        </header>

        <section className="h-[65vh] overflow-y-auto px-3 py-4">
          <div className="space-y-4">
            {messages.map((entry, index) =>
              entry.role === "user" ? (
                <UserBubble key={`${entry.role}-${index}`} text={entry.text} />
              ) : (
                <AssistantBubble
                  key={`${entry.role}-${index}`}
                  text={entry.text}
                  quickActions={index === messages.length - 1 ? quickActions : []}
                  onQuickAction={(actionId) => void handleQuickAction(actionId)}
                />
              ),
            )}
            {isLoading ? (
              <div className="flex items-center gap-2 px-1 text-xs text-slate-500">
                <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-500" />
                Procesando...
              </div>
            ) : null}
          </div>
        </section>

        {pendingUpdate ? (
          <section className="border-t border-slate-200 bg-white px-3 py-3">
            <p className="mb-2 text-xs font-medium text-slate-600">Que cambio queres aplicar al ticket?</p>
            <textarea
              value={updateFeedback}
              onChange={(event) => setUpdateFeedback(event.target.value)}
              rows={3}
              placeholder="Ejemplo: agrega criterio para metodos regionales"
              className="w-full rounded-2xl border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => {
                  setPendingUpdate(false);
                  setUpdateFeedback("");
                }}
                className="rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-600"
              >
                Cancelar
              </button>
              <button
                onClick={() => void handleUpdateSubmit()}
                className="rounded-full bg-indigo-600 px-3 py-1 text-xs font-medium text-white"
              >
                Aplicar cambio
              </button>
            </div>
          </section>
        ) : null}

        <footer className="border-t border-slate-200 bg-white px-3 py-3">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[11px] text-slate-500">
              {canAnswer ? "Responde la aclaracion" : "Describe tu necesidad"}
            </p>
            <p className="text-[11px] text-slate-400">{ticketId ? `Ticket: ${ticketId.slice(0, 8)}...` : "Sin ticket"}</p>
          </div>

          <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-2 py-2">
            <button className="h-8 w-8 rounded-full bg-white text-slate-500">＋</button>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleInputKeyDown}
              rows={1}
              placeholder="Escribe tu respuesta aqui..."
              className="max-h-24 flex-1 resize-none bg-transparent text-sm text-slate-700 focus:outline-none"
            />
            <button
              onClick={() => void handlePrimarySend()}
              disabled={isLoading || !message.trim()}
              className="h-9 w-9 rounded-xl bg-indigo-600 text-white disabled:opacity-50"
            >
              ▲
            </button>
          </div>

          <div className="mt-3 grid grid-cols-3 gap-2 text-center text-[11px] text-slate-500">
            <div className="rounded-xl bg-indigo-50 px-2 py-1 font-semibold text-indigo-600">Chat</div>
            <div className="rounded-xl bg-slate-100 px-2 py-1">Historial</div>
            <div className="rounded-xl bg-slate-100 px-2 py-1">Config</div>
          </div>
        </footer>
      </div>

      {ticketMarkdown ? <TicketModal markdown={ticketMarkdown} onClose={() => setTicketMarkdown("")} /> : null}

      <div className="mx-auto mt-4 w-full max-w-md rounded-2xl border border-slate-200 bg-white px-3 py-2 text-[11px] text-slate-500 shadow-sm">
        <p className="font-medium text-slate-600">Conexion</p>
        <input
          value={apiBase}
          onChange={(event) => setApiBase(event.target.value)}
          className="mt-1 w-full rounded-lg border border-slate-200 px-2 py-1 text-[11px] text-slate-700 focus:border-indigo-500 focus:outline-none"
        />
        {conversationTurns.length ? (
          <p className="mt-2 text-[11px] text-slate-400">Aclaraciones resueltas: {conversationTurns.length}</p>
        ) : null}
      </div>
    </main>
  );
}
