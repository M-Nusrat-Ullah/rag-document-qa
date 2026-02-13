"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK
)
async def health_check():
    """Check if the service is healthy."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@router.get("/ready")
async def readiness_check():
    """Check if the service is ready to handle requests."""
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Check if the service is alive."""
    return {"status": "alive"}