from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import DomainError
from app.models.database import get_db
from app.services.invoicing import process_midtrans_webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/midtrans")
async def midtrans_webhook(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """Public webhook receiver for Midtrans payment notifications."""
    try:
        res = await process_midtrans_webhook(db=db, payload=payload)
        return res
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())
