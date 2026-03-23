# Tickets Tool Backend - AI Agent Ruleset

> **Skills Reference**: For detailed patterns, use these skills:
> - [`fastapi-backend`](../skills/fastapi-backend/SKILL.md) - FastAPI route structure, models, services
> - [`tdd`](../skills/tdd/SKILL.md) - Test-first workflow and regression coverage

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| Creating Pydantic request/response models | `fastapi-backend` |
| Creating or modifying FastAPI routes | `fastapi-backend` |
| Fixing bug | `tdd` |
| Implementing feature | `tdd` |
| Refactoring code | `tdd` |
| Working on task | `tdd` |

## CRITICAL RULES - NON-NEGOTIABLE

### Routes
- ALWAYS: Keep route handlers thin and delegate AI/business logic to `services/`
- ALWAYS: Define `response_model` for public endpoints
- NEVER: Duplicate parsing/validation logic across endpoints

### Pydantic Models
- ALWAYS: Keep request/response schemas in `app/models.py`
- ALWAYS: Use explicit types and defaults (`Field(...)` when needed)
- NEVER: Return unvalidated free-form objects from routes

### Services
- ALWAYS: Wrap AI provider integration in service layer (`app/services/`)
- ALWAYS: Raise clear exceptions and let routes convert to HTTP errors
- NEVER: Call external providers directly from the frontend

### Error Handling
- ALWAYS: Log unexpected exceptions with context
- ALWAYS: Return safe generic 500 details for unhandled failures
- NEVER: Leak provider internals or stack traces in API responses

---

## DECISION TREES

### Where to place logic
```
Request parsing/HTTP status → routes.py
AI/provider communication    → services/*.py
Shared formatting/utilities → utils.py
```

### Endpoint shape
```
Single payload response        → one response model
Alternative flow (clarify/final) → Union response model
```

---

## TECH STACK

FastAPI | Pydantic | Uvicorn | Groq client | python-dotenv

---

## PROJECT STRUCTURE

```
backend/
├── main.py
└── app/
    ├── api.py
    ├── models.py
    ├── state_machine.py
    ├── prompts.py
    ├── repository.py
    ├── dependencies.py
    ├── utils.py
    ├── core/
    │   ├── config.py
    │   └── ai_client.py
    └── services/
        ├── ticket_service.py
        └── exceptions.py
```

---

## COMMANDS

```bash
# Setup
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Run API
uvicorn main:app --reload --app-dir backend
```

---

## QA CHECKLIST

- [ ] API boots with `uvicorn main:app --reload --app-dir backend`
- [ ] Endpoints return expected JSON shape for success and clarify flows
- [ ] Errors are handled without leaking internals

---

## NAMING CONVENTIONS

| Entity | Pattern | Example |
|--------|---------|---------|
| Route handler | `<action>_<entity>` | `analyze_request` |
| Service function | `<verb>_<target>` | `call_ai_and_parse` |
| Request model | `<Domain>Request` | `UserRequest` |
| Response model | `<Domain>Response` | `TicketResponse` |
