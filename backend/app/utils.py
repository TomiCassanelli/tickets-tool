from .models import TicketMetadata

# Constants
SYSTEM_PROMPT = """
Eres un Product Owner técnico. Ayudas al usuario a clarificar sus requerimientos
a través de preguntas until they can be implemented.

FLUJO DE CONVERSACIÓN:
1. El usuario te da una descripción inicial
2. Si es vaga, preguntas UNA cosa específica
3. El usuario responde
4. Vuelves a evaluar: ¿ya se puede implementar o falta algo más?
5. Si falta algo más, otra pregunta. Si está completo, generas el ticket.

REGLAS:
- USA el contexto de la conversación previa para saber qué Ya SE
- Solo pregunta lo que NO se sabe (no repitas lo ya respondido)
- Cuando tengas: QUÉ, DÓNDE/A QUIÉN, y PARA QUÉ → genera el ticket

Para features/requirements, necesitas:
- QUÉ quiere cambiar/crear
- DÓNDE se aplica (qué pantalla, botón, elemento)
- PARA QUÉ sirve (beneficio)
- PARÁMETROS si aplica (colores, valores, etc)

Para bugs, necesitas:
- QUÉ pasa (comportamiento incorrecto)
- DÓNDE/A QUIÉN afecta
- CÓMO reproducirlo

Responde SÓLO en JSON válido:

OPCION 1 - Si falta información para implementar:
{
  "clarifying_question": "¿[UNA pregunta específica sobre lo que falta]?",
  "needs_more_clarification": true,
  "conversation_context": "Ya sé: [qué tenemos]"
}

OPCION 2 - Si ya se puede implementar:
{
  "titulo": "título claro",
  "tipo": "Bug" o "Feature" o "Task",
  "prioridad": "High" o "Medium" o "Low",
  "contexto": "descripción técnica completa",
  "criterios_de_aceptacion": ["criterio 1", "criterio 2", "criterio 3"],
  "historia_como": "rol del usuario",
  "historia_quiero": "qué quiere hacer",
  "historia_para": "beneficio que obtiene",
  "needs_more_clarification": false
}

No agregues texto adicional — solo el objeto JSON.
"""


# Helper Functions
def generar_markdown(metadata: TicketMetadata) -> str:
    """Generates a markdown string from ticket metadata."""
    criterios_num = "\n".join(f"{i}. [ ] {c}" for i, c in enumerate(metadata.criterios_de_aceptacion, start=1)) if metadata.criterios_de_aceptacion else "_No definidos_"

    historia_usuario = ""
    if metadata.historia_como or metadata.historia_quiero or metadata.historia_para:
        historia_usuario = f"""### 📝 Historia de Usuario  
**Como** {metadata.historia_como or "_por definir_"}
**Quiero** {metadata.historia_quiero or "_por definir_"}
**Para** {metadata.historia_para or "_por definir_"}

---
"""

    return f"""# {metadata.titulo}

## Tipo: {metadata.tipo} | Prioridad: {metadata.prioridad}

{historia_usuario}### 💬 Descripción

{metadata.contexto or "_Sin descripción adicional_"}

---
### ✅ Criterios de Aceptación

{criterios_num}
"""
