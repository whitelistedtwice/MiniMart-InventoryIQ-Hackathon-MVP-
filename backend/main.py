from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import ai, analytics, dashboard, inventory, settings
from app.contracts.api import ApiError
from app.core.errors import InventoryIQError

load_dotenv()

app = FastAPI(title="InventoryIQ API")

# Layered API routes (contracts only in Phase 1)
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")


@app.exception_handler(InventoryIQError)
def handle_inventory_iq_error(request: Request, exc: InventoryIQError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ApiError(error=exc.code, message=exc.message, details=exc.details).model_dump(),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
