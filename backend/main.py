from fastapi import FastAPI

# Keep main.py as a lightweight entrypoint that wires the router
app = FastAPI(title="Pocket PO API")

try:
    from app import router as api_router
except Exception:
    # If package import fails, try relative fallback
    from .app import router as api_router  # type: ignore

app.include_router(api_router)