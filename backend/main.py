from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Keep main.py as a lightweight entrypoint that wires the router
app = FastAPI(title="Pocket PO API")

try:
    from app import router as api_router
except Exception:
    # If package import fails, try relative fallback
    from .app import router as api_router  # type: ignore

app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)