from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.invoicing import PaymentResponse, RecordPaymentRequest
from app.core.permissions import Permission
from app.domain.exceptions import DomainError
from app.models.database import get_db
from app.models.invoicing import Payment
from app.models.user import User
from app.services.invoicing import record_payment

router = APIRouter(prefix="/invoices/{invoice_id}/payments", tags=["Payments"])


@router.get("", response_model=list[PaymentResponse])
async def list_payments_for_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    stmt = (
        select(Payment)
        .where(Payment.invoice_id == invoice_id)
        .order_by(Payment.id.asc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def record_payment_endpoint(
    invoice_id: int,
    req: RecordPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.PAYMENT_RECORD)),
):
    try:
        payment = await record_payment(
            db=db,
            invoice_id=invoice_id,
            amount=req.amount,
            method=req.method,
            reference=req.reference,
            paid_at=None,
            user_id=current_user.id,
        )
        return payment
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())
