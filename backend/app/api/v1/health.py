from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str


@router.get("/health", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment="development",
        database="connected",
    )
