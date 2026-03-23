---
name: fastapi-backend
description: >
  FastAPI patterns for tickets-tool backend.
  Trigger: Working on backend/ API routes, models, services, and utilities.
license: MIT
metadata:
  author: tickets-tool
  version: "1.0"
  scope: [root, backend]
  auto_invoke:
    - "Creating or modifying FastAPI routes"
    - "Creating Pydantic request/response models"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Task
---

## When to Apply

Use this skill when:
- Creating or modifying FastAPI routes
- Defining Pydantic request/response models
- Adding business logic or AI integration services
- Working with the Groq client or external providers

---

## Critical Rules

### 1. Thin Routes, Thick Services

```python
# ✅ Route delegates to service
@router.post("/api/analyze")
async def analyze_request(req: UserRequest):
    ai_json = call_ai_and_parse(req.raw_text, MODEL_NAME)
    # ... parse and return

# ❌ Route contains business logic
@router.post("/api/analyze")
async def analyze_request(req: UserRequest):
    client = get_ai_client()
    response = client.chat.completions.create(...)
    # ... complex logic in route
```

### 2. Explicit Response Models

```python
# ✅ Always define response_model
@router.post("/api/analyze", response_model=TicketResponse)
async def analyze_request(req: UserRequest):
    ...

# ✅ Union for alternative flows
@router.post("/api/analyze", response_model=Union[TicketResponse, ClarifyResponse])
async def analyze_request(req: UserRequest):
    ...
```

### 3. Pydantic Models in Dedicated File

```python
# app/models.py
class TicketMetadata(BaseModel):
    titulo: str = Field(..., description="Short and clear title")
    tipo: str = Field(..., description="Must be 'Bug', 'Feature' or 'Task'")

class TicketResponse(BaseModel):
    metadata: TicketMetadata
    markdown: str
```

### 4. Proper Error Handling

```python
# ✅ Log and raise generic error
except Exception as e:
    logger.exception("Unexpected error in analyze_request")
    raise HTTPException(status_code=500, detail="Internal server error")

# ✅ Re-raise HTTP exceptions
except HTTPException:
    raise
```

---

## Decision Tree

```text
Adding new endpoint?      -> Add to routes.py, create models in models.py
Business logic/AI call?    -> Create service in services/ticket_service.py
Shared utilities?         -> Add to utils.py
Need validation?          -> Use Pydantic Field(...) with description
```

---

## Project Structure

```
backend/
├── main.py              # App entry point
└── app/
    ├── routes.py        # Route handlers (thin)
    ├── models.py        # Pydantic models
    ├── utils.py         # Shared utilities
    └── services/
        └── ticket_service.py  # Business logic
```

---

## Service Pattern

```python
def call_ai_and_parse(raw_text: str, model_name: str) -> dict:
    """Service function that wraps external provider."""
    client = get_ai_client()
    try:
        response = client.chat.completions.create(...)
    except Exception as e:
        logger.exception("Provider call failed")
        raise

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        logger.exception("Invalid JSON from provider")
        raise
```

---

## Commands

```bash
# Setup
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# Run API
uvicorn main:app --reload --app-dir backend
```

---

## Naming Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Route handler | `<action>_<entity>` | `analyze_request` |
| Service function | `<verb>_<target>` | `call_ai_and_parse` |
| Request model | `<Domain>Request` | `UserRequest` |
| Response model | `<Domain>Response` | `TicketResponse` |
