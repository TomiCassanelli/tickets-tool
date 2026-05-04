import type { ConversationTurn } from "../types/ticket";

interface ConversationTimelineProps {
  turns: ConversationTurn[];
}

export function ConversationTimeline({ turns }: ConversationTimelineProps) {
  if (!turns.length) {
    return null;
  }

  return (
    <div className="mb-4 space-y-2 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      {turns.map((turn, index) => (
        <div key={`${index}-${turn.question}`} className="space-y-1 rounded-lg bg-slate-50 p-3">
          <p className="text-sm text-slate-700">
            <span className="font-semibold">Pregunta:</span> {turn.question}
          </p>
          <p className="text-sm text-slate-800">
            <span className="font-semibold">Respuesta:</span> {turn.answer}
          </p>
        </div>
      ))}
    </div>
  );
}
