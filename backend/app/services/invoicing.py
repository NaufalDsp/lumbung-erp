import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_token
from app.domain.enums import (
    DocType,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
    SalesOrderStatus,
)
from app.domain.exceptions import DomainError
from app.domain.state_machine import InvoiceStateMachine
from app.domain.values import BasisPoints, Money
from app.integrations.payment import get_payment_gateway, verify_midtrans_signature
from app.models.company import Company
from app.models.invoicing import (
    Invoice,
    InvoiceLine,
    Payment,
    PaymentLink,
    WebhookEvent,
)
from app.models.master import Customer
from app.models.sales import Delivery, DeliveryLine, SalesOrder
from app.services.audit import record_audit_log
from app.services.stock import get_next_doc_number


async def create_invoice_from_deliveries(
    db: AsyncSession,
    delivery_ids: list[int],
    notes: str | None,
    user_id: int,
) -> Invoice:
    """Generates a Draft Invoice from one or more unbilled deliveries belonging to the same customer."""
    if not delivery_ids:
        raise DomainError(
            "PENGIRIMAN_KOSONG", "Minimal satu surat jalan harus dipilih untuk difakturkan")

    stmt = (
        select(Delivery)
        .options(
            selectinload(Delivery.customer),
            selectinload(Delivery.lines).selectinload(DeliveryLine.so_line),
        )
        .where(Delivery.id.in_(delivery_ids))
    )
    deliveries = (await db.execute(stmt)).scalars().all()

    if len(deliveries) != len(delivery_ids):
        raise DomainError("PENGIRIMAN_TIDAK_DITEMUKAN",
                          "Beberapa surat jalan tidak ditemukan")

    customer_ids = {d.customer_id for d in deliveries}
    if len(customer_ids) > 1:
        raise DomainError(
            "PELANGGAN_BERBEDA",
            "Semua surat jalan dalam satu faktur harus berasal dari pelanggan yang sama",
        )

    customer_id = customer_ids.pop()

    # Collect delivery lines and ensure none are already invoiced
    deliv_line_ids = [line.id for d in deliveries for line in d.lines]
    existing_invoiced = await db.execute(
        select(InvoiceLine.delivery_line_id).where(
            InvoiceLine.delivery_line_id.in_(deliv_line_ids))
    )
    already_invoiced_ids = set(existing_invoiced.scalars().all())
    if already_invoiced_ids:
        raise DomainError(
            "SUDAH_DIFAKTURKAN",
            f"Baris pengiriman ID {already_invoiced_ids} sudah pernah difakturkan sebelumnya",
        )

    # Calculate integer lines and subtotal
    subtotal = 0
    invoice_lines: list[InvoiceLine] = []

    for d in deliveries:
        for d_line in d.lines:
            so_line = d_line.so_line
            gross = d_line.qty * so_line.unit_price
            bp = BasisPoints(so_line.discount_bp)
            discount = bp.calculate_amount(Money(gross)).amount
            line_subtotal = gross - discount

            subtotal += line_subtotal
            invoice_lines.append(
                InvoiceLine(
                    delivery_line_id=d_line.id,
                    product_id=d_line.product_id,
                    qty=d_line.qty,
                    unit_price=so_line.unit_price,
                    discount_bp=so_line.discount_bp,
                    subtotal=line_subtotal,
                )
            )

    # Calculate PPN 11% using company tax rate basis points
    company = (await db.execute(select(Company).where(Company.id == 1))).scalar_one_or_none()
    tax_rate_bp = company.tax_rate_bp if company else 1100
    tax = BasisPoints(tax_rate_bp).calculate_amount(Money(subtotal)).amount
    total = subtotal + tax

    invoice = Invoice(
        customer_id=customer_id,
        status=InvoiceStatus.DRAF.value,
        subtotal=subtotal,
        tax=tax,
        total=total,
        notes=notes,
        created_by=user_id,
    )
    db.add(invoice)
    await db.flush()

    for line in invoice_lines:
        line.invoice_id = invoice.id
        db.add(line)

    await record_audit_log(
        db=db,
        entity="invoice",
        entity_id=invoice.id,
        action="create_draft",
        actor_id=user_id,
        from_status=None,
        to_status=invoice.status,
        diff={"subtotal": subtotal, "tax": tax, "total": total},
    )

    await db.commit()
    return invoice


async def issue_invoice(
    db: AsyncSession,
    invoice_id: int,
    user_id: int,
) -> Invoice:
    """Issues an invoice, generating sequential INV-YYYY-XXXXXX number and calculating due date."""
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.customer))
        .where(Invoice.id == invoice_id)
        .with_for_update()
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if not invoice:
        raise DomainError("FAKTUR_TIDAK_DITEMUKAN",
                          f"Faktur ID {invoice_id} tidak ditemukan")

    InvoiceStateMachine.validate_transition(
        current=InvoiceStatus(invoice.status),
        target=InvoiceStatus.TERBIT,
    )

    inv_number = await get_next_doc_number(db, DocType.INV)
    now = datetime.now(timezone.utc)
    terms_days = invoice.customer.terms_days if invoice.customer else 30
    due_date = now + timedelta(days=terms_days)

    old_status = invoice.status
    invoice.number = inv_number
    invoice.status = InvoiceStatus.TERBIT.value
    invoice.issued_at = now
    invoice.due_at = due_date

    await record_audit_log(
        db=db,
        entity="invoice",
        entity_id=invoice.id,
        action="issue",
        actor_id=user_id,
        from_status=old_status,
        to_status=invoice.status,
        diff={"number": inv_number, "due_at": due_date.isoformat()},
    )

    await db.commit()
    return invoice


async def void_invoice(
    db: AsyncSession,
    invoice_id: int,
    user_id: int,
) -> Invoice:
    """Voids an invoice (only permitted if no payments have been recorded)."""
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.payments))
        .where(Invoice.id == invoice_id)
        .with_for_update()
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if not invoice:
        raise DomainError("FAKTUR_TIDAK_DITEMUKAN",
                          f"Faktur ID {invoice_id} tidak ditemukan")

    has_payments = any(
        p.status == PaymentStatus.BERHASIL.value for p in invoice.payments)
    InvoiceStateMachine.validate_transition(
        current=InvoiceStatus(invoice.status),
        target=InvoiceStatus.VOID,
        has_payments=has_payments,
    )

    old_status = invoice.status
    invoice.status = InvoiceStatus.VOID.value

    await record_audit_log(
        db=db,
        entity="invoice",
        entity_id=invoice.id,
        action="void",
        actor_id=user_id,
        from_status=old_status,
        to_status=invoice.status,
    )

    await db.commit()
    return invoice


async def record_payment(
    db: AsyncSession,
    invoice_id: int,
    amount: int,
    method: PaymentMethod,
    reference: str | None,
    paid_at: datetime | None,
    user_id: int | None,
) -> Payment:
    """Records a payment and deterministically updates invoice and parent order statuses."""
    stmt = (
        select(Invoice)
        .options(
            selectinload(Invoice.payments),
            selectinload(Invoice.lines).selectinload(
                InvoiceLine.delivery_line).selectinload(DeliveryLine.delivery),
        )
        .where(Invoice.id == invoice_id)
        .with_for_update()
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if not invoice:
        raise DomainError("FAKTUR_TIDAK_DITEMUKAN",
                          f"Faktur ID {invoice_id} tidak ditemukan")

    if invoice.status not in (InvoiceStatus.TERBIT.value, InvoiceStatus.SEBAGIAN_DIBAYAR.value):
        raise DomainError(
            "STATUS_FAKTUR_TIDAK_VALID",
            f"Pembayaran hanya dapat dicatat untuk faktur berstatus Terbit atau Sebagian Dibayar (saat ini: {invoice.status})",
        )

    current_paid = sum(
        p.amount for p in invoice.payments if p.status == PaymentStatus.BERHASIL.value
    )
    remaining_balance = invoice.total - current_paid

    if amount <= 0:
        raise DomainError("JUMLAH_TIDAK_VALID", "Jumlah pembayaran harus > 0")

    if amount > remaining_balance:
        raise DomainError(
            "LEBIH_BAYAR",
            f"Jumlah pembayaran (Rp {amount:,}) melebihi sisa tagihan (Rp {remaining_balance:,})",
        )

    payment = Payment(
        invoice_id=invoice.id,
        amount=amount,
        method=method.value,
        status=PaymentStatus.BERHASIL.value,
        reference=reference,
        paid_at=paid_at or datetime.now(timezone.utc),
        created_by=user_id,
    )
    db.add(payment)
    await db.flush()

    new_total_paid = current_paid + amount
    old_status = invoice.status
    if new_total_paid >= invoice.total:
        invoice.status = InvoiceStatus.LUNAS.value
    else:
        invoice.status = InvoiceStatus.SEBAGIAN_DIBAYAR.value

    # If Invoice is LUNAS, check if the parent Sales Order is now completely finished (PRD 7.3)
    if invoice.status == InvoiceStatus.LUNAS.value:
        so_ids = {
            line.delivery_line.delivery.so_id for line in invoice.lines if line.delivery_line and line.delivery_line.delivery}
        for so_id in so_ids:
            so_stmt = select(SalesOrder).where(
                SalesOrder.id == so_id).with_for_update()
            so = (await db.execute(so_stmt)).scalar_one_or_none()
            if so and so.status == SalesOrderStatus.TERKIRIM.value:
                # Check if all deliveries for this SO are fully invoiced & paid
                so.status = SalesOrderStatus.SELESAI.value

    await record_audit_log(
        db=db,
        entity="invoice",
        entity_id=invoice.id,
        action="payment_received",
        actor_id=user_id,
        from_status=old_status,
        to_status=invoice.status,
        diff={"payment_id": payment.id,
              "amount": amount, "method": method.value},
    )

    await db.commit()
    return payment


async def create_payment_link(
    db: AsyncSession,
    invoice_id: int,
    user_id: int,
) -> tuple[str, datetime, str | None]:
    """Generates an opaque random token for public invoice access and Midtrans Snap."""
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.customer), selectinload(Invoice.payments))
        .where(Invoice.id == invoice_id)
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if not invoice or not invoice.number:
        raise DomainError("FAKTUR_TIDAK_DITEMUKAN",
                          "Faktur belum diterbitkan atau tidak ditemukan")

    current_paid = sum(
        p.amount for p in invoice.payments if p.status == PaymentStatus.BERHASIL.value)
    balance_due = invoice.total - current_paid
    if balance_due <= 0:
        raise DomainError("FAKTUR_SUDAH_LUNAS", "Faktur ini sudah lunas")

    raw_token = secrets.token_urlsafe(32)
    tok_hash = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=24)
    midtrans_order_id = f"LMB-{invoice.number}-{int(now.timestamp())}"

    gateway = get_payment_gateway()
    snap_resp = await gateway.create_snap_transaction(
        order_id=midtrans_order_id,
        gross_amount=balance_due,
        customer_name=invoice.customer.name if invoice.customer else "Pelanggan",
        customer_email=invoice.customer.email if invoice.customer else None,
    )

    link = PaymentLink(
        invoice_id=invoice.id,
        token_hash=tok_hash,
        midtrans_order_id=midtrans_order_id,
        expires_at=expires_at,
    )
    db.add(link)
    await db.commit()

    return raw_token, expires_at, snap_resp.get("token")


async def process_midtrans_webhook(
    db: AsyncSession,
    payload: dict[str, Any],
) -> dict[str, str]:
    """Idempotently processes Midtrans payment webhook with signature verification."""
    order_id = payload.get("order_id", "")
    status_code = payload.get("status_code", "")
    gross_amount = payload.get("gross_amount", "")
    signature_key = payload.get("signature_key", "")
    tx_status = payload.get("transaction_status", "")
    tx_time = payload.get("transaction_time", str(
        datetime.now(timezone.utc).timestamp()))

    if not order_id or not status_code or not gross_amount or not signature_key:
        raise DomainError("PAYLOAD_TIDAK_LENGKAP",
                          "Parameter webhook Midtrans tidak lengkap")

    # 1. Constant-time Signature Verification (PRD 9.2)
    if settings.MIDTRANS_SERVER_KEY:
        is_valid = verify_midtrans_signature(
            order_id=order_id,
            status_code=status_code,
            gross_amount=gross_amount,
            signature_key=signature_key,
        )
        if not is_valid:
            raise DomainError("TANDA_TANGAN_TIDAK_COCOK",
                              "Verifikasi signature Midtrans gagal")

    # 2. Idempotency Check (PRD 9.2 & 10.2)
    event_key = f"{order_id}_{tx_status}_{tx_time}"
    existing_event = await db.execute(
        select(WebhookEvent).where(WebhookEvent.provider ==
                                   "midtrans", WebhookEvent.event_key == event_key)
    )
    if existing_event.scalar_one_or_none():
        return {"status": "duplicate_ignored"}

    # 3. Locate associated PaymentLink & Invoice
    link_stmt = select(PaymentLink).where(
        PaymentLink.midtrans_order_id == order_id)
    link = (await db.execute(link_stmt)).scalar_one_or_none()
    if not link:
        # Record unlinked event
        db.add(WebhookEvent(provider="midtrans", event_key=event_key,
               payload=payload, result="unlinked"))
        await db.commit()
        return {"status": "unlinked_order"}

    # 4. Handle successful settlement or capture
    if tx_status in ("settlement", "capture"):
        amount_int = int(float(gross_amount))
        await record_payment(
            db=db,
            invoice_id=link.invoice_id,
            amount=amount_int,
            method=PaymentMethod.MIDTRANS,
            reference=f"Midtrans-{order_id}",
            paid_at=datetime.now(timezone.utc),
            user_id=None,
        )
        result_str = "payment_settled"
    else:
        result_str = f"status_{tx_status}"

    # 5. Persist webhook event for idempotency guarantee
    db.add(WebhookEvent(provider="midtrans", event_key=event_key,
           payload=payload, result=result_str))
    await db.commit()

    return {"status": result_str}
