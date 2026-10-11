from datetime import datetime, timezone
from typing import Any
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.domain.enums import InvoiceStatus, PaymentMethod, PaymentStatus
from app.models.base import Base, TimestampMixin
from app.models.master import Customer, Product
from app.models.sales import DeliveryLine


class Invoice(Base, TimestampMixin):
    """Customer Invoice (INV) document generated from fulfilled deliveries."""
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str | None] = mapped_column(
        String(50), unique=True, index=True, nullable=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(30),
        default=InvoiceStatus.DRAF.value,
        nullable=False,
        index=True,
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True)
    subtotal: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    tax: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    customer: Mapped[Customer] = relationship("Customer")
    lines: Mapped[list["InvoiceLine"]] = relationship(
        "InvoiceLine",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    payment_links: Mapped[list["PaymentLink"]] = relationship(
        "PaymentLink",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    @property
    def is_overdue(self) -> bool:
        """Derived property: true if issued/partially paid and past due_at."""
        if self.status in (InvoiceStatus.TERBIT.value, InvoiceStatus.SEBAGIAN_DIBAYAR.value) and self.due_at:
            return datetime.now(timezone.utc) > self.due_at
        return False


class InvoiceLine(Base):
    """Line item on an Invoice directly referencing a delivered shipment item.

    Database unique constraint ensures a delivery line can never be invoiced twice.
    """
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    delivery_line_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("delivery_lines.id"),
        nullable=False,
        unique=True,  # Constraint: uq_invoice_line_delivery_line
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    discount_bp: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)
    subtotal: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)

    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="lines")
    delivery_line: Mapped[DeliveryLine] = relationship("DeliveryLine")
    product: Mapped[Product] = relationship("Product")


class Payment(Base):
    """Payment recorded against an invoice (manual bank transfer or Midtrans)."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    method: Mapped[str] = mapped_column(
        String(30), nullable=False, default=PaymentMethod.TRANSFER.value)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=PaymentStatus.BERHASIL.value)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    invoice: Mapped[Invoice] = relationship(
        "Invoice", back_populates="payments")


class PaymentLink(Base):
    """Secure public payment link token for Midtrans Snap."""
    __tablename__ = "payment_links"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False)
    midtrans_order_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    invoice: Mapped[Invoice] = relationship(
        "Invoice", back_populates="payment_links")


class WebhookEvent(Base):
    """Idempotent record of processed third-party webhook events."""
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="midtrans")
    event_key: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    result: Mapped[str] = mapped_column(
        String(50), nullable=False, default="success")

    __table_args__ = (
        UniqueConstraint("provider", "event_key", name="uq_webhook_event_key"),
    )
