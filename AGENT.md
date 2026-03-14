# 📱 Product Owner de Bolsillo (PO Agent) - Master Context & Architecture

## 🎯 1. Visión Global del Producto
El "Product Owner de Bolsillo" es una herramienta Full Stack potenciada por Inteligencia Artificial Generativa. Su propósito principal es resolver la fricción en el ciclo de desarrollo de software: **transformar requerimientos caóticos, informales y no estructurados (texto crudo o transcripciones de audio) en tickets de trabajo perfectamente tipados y formateados en Markdown.**

El objetivo es lograr un MVP sólido que procese el caos y devuelva estructura, sentando las bases para futuras integraciones complejas (RAG para detección de duplicados con ChromaDB, Tool Calling para integraciones nativas con GitHub/Jira, y soporte para modelos locales vía Ollama).

## 🏛️ 2. Arquitectura del Sistema y Flujo de Datos
El sistema está estrictamente dividido en dos dominios que operan de forma independiente. **Bajo ninguna circunstancia se debe mezclar la lógica de la interfaz con la lógica de negocio.**

### 🧠 Fase 1: Extracción y Transformación (La Regla de Oro)
El motor principal utiliza un patrón de **"Extracción de Datos Pura -> Transformación en Código"** para garantizar cero fallos en el tipado:
1. **Input:** El sistema recibe texto caótico y sin mucha explicación.
2. **Extracción (LLM):** Se envía a la API de Groq (modelo `llama-3.1-8b-instant`). Se exige un formato de salida estricto (`Structured Outputs`) utilizando esquemas de `Pydantic`. El LLM *solo* extrae la metadata pura y estructurada en JSON (Ej: `titulo`, `tipo`, `prioridad`, `contexto`, `criterios_aceptacion` como lista).
3. **Transformación (Python):** El backend toma ese JSON seguro y predecible, y utiliza lógica determinista de Python para ensamblar el texto final en formato **Markdown** (con sus respectivos `#`, `##`, y viñetas de `- [ ]`).
4. **Output:** El backend responde al cliente con la metadata original y el Markdown ya renderizado y listo para usar.

## 🛠️ 3. Dominios Técnicos y Stack

### Dominio A: Backend (`/backend`)
- **Stack:** Python 3, FastAPI, Pydantic, Uvicorn, pytest.
- **Responsabilidad:** Manejar la comunicación con la API de Groq, validar esquemas, manejar errores de red y ensamblar el Markdown.
- **Reglas del Dominio:**
  - Tipado estricto obligatorio en cada endpoint.
  - Manejo de excepciones robusto (`HTTPException`) para timeouts o fallos del LLM.
  - TDD (Test-Driven Development) recomendado. Todo endpoint debe ser testeable y resistir inputs vacíos o defectuosos.

### Dominio B: Frontend (`/frontend`)
- **Stack:** React Native, Expo.
- **Responsabilidad:** Interfaz táctica "Mobile-First". Proveer una experiencia de usuario sin fricciones para el ingreso rápido de requerimientos.
- **Reglas del Dominio:**
  - Diseño minimalista: Un `TextInput` expansible, un botón de acción principal y un área de visualización.
  - Manejo de estado de UI indispensable: Mostrar `ActivityIndicator` (loading) durante las llamadas a la red.
  - Renderizado limpio del Markdown devuelto por el backend.

## 🤖 4. Directivas Estrictas para el Agente (OpenCode)
Cuando operes en este proyecto, asume el rol de un **Ingeniero en Sistemas Senior** y obedece estas directivas:

1. **Conciencia de Contexto:** Antes de crear o modificar un archivo, verifica tu directorio de trabajo actual (`pwd`). Aplica las reglas de React Native/Expo SOLO si estás en `/frontend`. Aplica las reglas de FastAPI/Python SOLO si estás en `/backend`.
2. **Aprovechamiento de Skills:** Utiliza las skills instaladas en `.agents/skills/` (FastAPI router, pytest, React Native best practices, Data Fetching) de forma proactiva.
3. **Código Defensivo:** Nunca asumas que la API externa o el input del usuario son seguros. Valida todo.
4. **Idioma:** El codigo, los tipos de datos, la estructura y demás deben estar en **Ingles**. Los comentarios en el código, la documentación de la API y las respuestas del LLM deben estar en **Español**.
5. **No Alucinar Markdown en JSON:** Recuerda la Regla de Oro de la Fase 1. No le pidas al LLM que redacte Markdown dentro de las propiedades del JSON. El LLM extrae arrays y strings simples; Python los formatea.