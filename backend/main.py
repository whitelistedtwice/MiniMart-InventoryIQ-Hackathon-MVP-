import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import ai, analytics, dashboard, inventory, settings
from app.contracts.api import ApiError
from app.core.errors import InventoryIQError

load_dotenv()

app = FastAPI(title="InventoryIQ API")

# Minimal CORS for local frontend development (override via env if needed).
_origins = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Layered API routes
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")

_STATUS_BY_ERROR = {
    "validation_error": 422,
    "not_found": 404,
    "data_access_error": 502,
    "processing_error": 422,
    "analytics_error": 422,
    "recommendation_error": 422,
    "ai_context_error": 500,
    "gemini_error": 502,
}


@app.exception_handler(InventoryIQError)
def handle_inventory_iq_error(request: Request, exc: InventoryIQError) -> JSONResponse:
    return JSONResponse(
        status_code=_STATUS_BY_ERROR.get(exc.code, 500),
        content=ApiError(error=exc.code, message=exc.message, details=exc.details).model_dump(),
    )


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # Never leak stack traces or internals.
    return JSONResponse(
        status_code=500,
        content=ApiError(error="internal_error", message="Unexpected server error").model_dump(),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
