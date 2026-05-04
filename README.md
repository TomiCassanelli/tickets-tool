# Tickets Tool

Una herramienta simple para generar tickets técnicos usando IA.

## Tech Stack

- **Backend:** FastAPI · Python · Groq (Llama 3) · Pydantic v2
- **Frontend:** Next.js 14 · React 18 · TypeScript · Tailwind CSS 3

## Cómo funciona

1. Escribí tu idea o problema en el chat.
2. La IA te hace una sola pregunta si falta información.
3. Generá un ticket estructurado (tipo, prioridad, criterios, riesgos, etc.).
4. Podés actualizarlo o finalizarlo.

## Estructura

```
tickets-tool/
├── backend/     (API con FastAPI + IA)
└── frontend/    (Interfaz de chat con Next.js)
```

## Ejecución

**Backend:**
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
uvicorn main:app --reload --app-dir backend
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Abrí:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
