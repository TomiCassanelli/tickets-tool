import type { ToolCallingMeta } from "../types/ticket";

interface StatusBadgeProps {
  meta: ToolCallingMeta | null;
  version: number | null;
}

export function StatusBadge({ meta, version }: StatusBadgeProps) {
  if (!meta) {
    return <div className="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-700">Sin estado</div>;
  }

  return (
    <div className="space-y-2">
      <div className="rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-700">
        {meta.status} | intent: {meta.intent}
      </div>
      <div className="text-xs text-slate-600">
        Siguiente paso: {meta.next_allowed_actions[0] || "Sin acciones disponibles"}
      </div>
      {version !== null ? <div className="text-xs font-medium text-emerald-700">Version actual: {version}</div> : null}
    </div>
  );
}
