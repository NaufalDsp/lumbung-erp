from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import get_db
from app.services.seed import reset_demo_data

router = APIRouter(prefix="/system", tags=["System Jobs"])


@router.post("/reset-demo")
async def system_reset_demo(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_internal_secret: Annotated[str | None,
                                 Header(alias="X-Internal-Secret")] = None,
) -> dict[str, str]:
    """Nightly cron job endpoint to reset demo environment deterministically."""
    # Validate internal secret or demo mode
    if settings.INTERNAL_JOB_SECRET and x_internal_secret != settings.INTERNAL_JOB_SECRET:
        if not settings.DEMO_MODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "SECRET_TIDAK_VALID",
                        "message": "Autentikasi tugas internal tidak valid"},
            )

    return await reset_demo_data(db)
