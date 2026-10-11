from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permission
from app.api.v1.schemas.invoicing import (
    CreateInvoiceRequest,
    InvoiceResponse,
    PaymentLinkResponse,
)
from app.domain.enums import UserRole
from app.domain.exceptions import DomainError
from app.models.base import get_db
from app.models.invoicing import Invoice
from app.models.user import User
from app.services.invoicing import (
    create_invoice_from_deliveries,
    create_payment_link,
    issue_invoice,
    void_invoice,
)

router = APIRouter(prefix="/invoices", tags=["Invoicing"])


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    status_filter: str | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.lines), selectinload(Invoice.payments))
        .order_by(Invoice.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if status_filter:
        stmt = stmt.where(Invoice.status == status_filter)
    if customer_id:
        stmt = stmt.where(Invoice.customer_id == customer_id)

    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    req: CreateInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("create", "invoice")),
):
    try:
        inv = await create_invoice_from_deliveries(
            db=db,
            delivery_ids=req.delivery_ids,
            notes=req.notes,
            user_id=current_user.id,
        )
        # Reload with lines
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines), selectinload(Invoice.payments))
            .where(Invoice.id == inv.id)
        )
        return (await db.execute(stmt)).scalar_one()
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.lines), selectinload(Invoice.payments))
        .where(Invoice.id == invoice_id)
    )
    inv = (await db.execute(stmt)).scalar_one_or_none()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FAKTUR_TIDAK_DITEMUKAN",
                    "message": "Faktur tidak ditemukan"},
        )
    return inv


@router.post("/{invoice_id}/issue", response_model=InvoiceResponse)
async def issue_invoice_endpoint(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("issue", "invoice")),
):
    try:
        inv = await issue_invoice(db=db, invoice_id=invoice_id, user_id=current_user.id)
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines), selectinload(Invoice.payments))
            .where(Invoice.id == inv.id)
        )
        return (await db.execute(stmt)).scalar_one()
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice_endpoint(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("void", "invoice")),
):
    try:
        inv = await void_invoice(db=db, invoice_id=invoice_id, user_id=current_user.id)
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines), selectinload(Invoice.payments))
            .where(Invoice.id == inv.id)
        )
        return (await db.execute(stmt)).scalar_one()
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())


@router.post("/{invoice_id}/payment-link", response_model=PaymentLinkResponse)
async def create_payment_link_endpoint(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("create", "payment")),
):
    try:
        raw_token, expires_at, snap_token = await create_payment_link(
            db=db, invoice_id=invoice_id, user_id=current_user.id
        )
        return PaymentLinkResponse(
            token=raw_token,
            expires_at=expires_at,
            payment_url=f"/bayar/{raw_token}",
            snap_token=snap_token,
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.to_dict())
