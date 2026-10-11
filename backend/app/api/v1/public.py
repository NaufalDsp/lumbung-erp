from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.schemas.invoicing import PublicInvoiceLine, PublicInvoiceResponse
from app.core.security import hash_token
from app.domain.enums import PaymentStatus
from app.models.base import get_db
from app.models.company import Company
from app.models.invoicing import Invoice, InvoiceLine, PaymentLink
from app.models.master import Product

router = APIRouter(prefix="/public", tags=["Public Portal"])


@router.get("/invoices/{token}", response_model=PublicInvoiceResponse)
async def get_public_invoice(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves invoice details for public payment and customer viewing using raw 128-bit token."""
    tok_hash = hash_token(token)
    stmt = (
        select(PaymentLink)
        .options(
            selectinload(PaymentLink.invoice)
            .selectinload(Invoice.customer),
            selectinload(PaymentLink.invoice)
            .selectinload(Invoice.payments),
            selectinload(PaymentLink.invoice)
            .selectinload(Invoice.lines)
            .selectinload(InvoiceLine.product),
        )
        .where(PaymentLink.token_hash == tok_hash)
    )
    link = (await db.execute(stmt)).scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "LINK_TIDAK_DITEMUKAN",
                    "message": "Tautan pembayaran tidak valid"},
        )

    now = datetime.now(timezone.utc)
    # Ensure link.expires_at is timezone-aware
    expires_at = link.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"code": "LINK_KADALUWARSA",
                    "message": "Tautan pembayaran sudah kedaluwarsa (masa berlaku 24 jam)"},
        )

    inv = link.invoice
    company = (await db.execute(select(Company).where(Company.id == 1))).scalar_one_or_none()
    company_name = company.name if company else "Lumbung ERP"

    current_paid = sum(
        p.amount for p in inv.payments if p.status == PaymentStatus.BERHASIL.value)
    balance_due = max(0, inv.total - current_paid)

    lines = [
        PublicInvoiceLine(
            product_name=line.product.name if line.product else "Barang",
            qty=line.qty,
            unit_price=line.unit_price,
            subtotal=line.subtotal,
        )
        for line in inv.lines
    ]

    return PublicInvoiceResponse(
        number=inv.number or f"DRAF-{inv.id}",
        customer_name=inv.customer.name if inv.customer else "Pelanggan",
        company_name=company_name,
        status=inv.status,
        issued_at=inv.issued_at,
        due_at=inv.due_at,
        subtotal=inv.subtotal,
        tax=inv.tax,
        total=inv.total,
        balance_due=balance_due,
        lines=lines,
        snap_token=None,
    )
