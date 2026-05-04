import type { TicketMetadata } from "../types/ticket";

export function buildTicketMarkdown(ticket: TicketMetadata): string {
  const acceptance = ticket.criterios_de_aceptacion.map((item) => `- ${item}`).join("\n");
  const risks = ticket.riesgos.map((item) => `- ${item}`).join("\n");
  const done = ticket.definition_of_done.map((item) => `- ${item}`).join("\n");

  return [
    `# ${ticket.titulo}`,
    "",
    `- **Tipo:** ${ticket.tipo}`,
    `- **Prioridad:** ${ticket.prioridad}`,
    "",
    "## Contexto",
    ticket.contexto,
    "",
    "## Historia de usuario",
    `- **Como** ${ticket.historia_como}`,
    `- **Quiero** ${ticket.historia_quiero}`,
    `- **Para** ${ticket.historia_para}`,
    "",
    "## Criterios de aceptacion",
    acceptance || "- Sin criterios",
    "",
    "## Alcance",
    ticket.alcance || "Sin definir",
    "",
    "## Riesgos",
    risks || "- Sin riesgos",
    "",
    "## Definition of Done",
    done || "- Sin DoD",
    "",
    "## Notas tecnicas",
    ticket.notas_tecnicas || "Sin notas",
  ].join("\n");
}
