"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

interface TicketDrawerProps {
  markdown: string;
  onClose: () => void;
}

export function TicketDrawer({ markdown, onClose }: TicketDrawerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(markdown);

  async function handleCopy() {
    await navigator.clipboard.writeText(value);
  }

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full flex-col bg-white shadow-2xl md:w-[560px]">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h3 className="text-lg font-semibold text-slate-900">Ticket Preview</h3>
        <div className="flex gap-2">
          <button onClick={handleCopy} className="rounded-lg bg-sky-600 px-3 py-1.5 text-sm text-white">
            Copiar
          </button>
          <button
            onClick={() => setIsEditing((prev) => !prev)}
            className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-700"
          >
            {isEditing ? "Ver" : "Editar"}
          </button>
          <button onClick={onClose} className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-700">
            Cerrar
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {isEditing ? (
          <textarea
            value={value}
            onChange={(event) => setValue(event.target.value)}
            className="min-h-[520px] w-full rounded-xl border border-slate-300 p-3 font-mono text-sm focus:border-sky-500 focus:outline-none"
          />
        ) : (
          <article className="prose prose-sm max-w-none">
            <ReactMarkdown>{value}</ReactMarkdown>
          </article>
        )}
      </div>
    </div>
  );
}
