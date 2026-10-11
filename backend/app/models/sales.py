from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import SalesOrderStatus
from app.models.base import Base, TimestampMixin
from app.models.master import Customer, Product


class SalesOrder(Base, TimestampMixin):
    """Sales Order (SO) document entity representing customer orders."""
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str | None] = mapped_column(
        String(50), unique=True, index=True, nullable=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default=SalesOrderStatus.DRAF.value,
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    customer: Mapped[Customer] = relationship("Customer")
    lines: Mapped[list["SalesOrderLine"]] = relationship(
        "SalesOrderLine",
        back_populates="sales_order",
        cascade="all, delete-orphan",
    )
    deliveries: Mapped[list["Delivery"]] = relationship(
        "Delivery",
        back_populates="sales_order",
    )


class SalesOrderLine(Base):
    """Line item in a Sales Order with quantity, unit price, and discount basis points."""
    __tablename__ = "sales_order_lines"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    so_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    discount_bp: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)  # basis points (e.g. 500 = 5%)
    delivered_qty: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    sales_order: Mapped[SalesOrder] = relationship(
        "SalesOrder", back_populates="lines")
    product: Mapped[Product] = relationship("Product")


class Delivery(Base):
    """Delivery Order (DO) / Surat Jalan document representing physical shipment."""
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    so_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        "sales_orders.id"), nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sales_order: Mapped[SalesOrder] = relationship(
        "SalesOrder", back_populates="deliveries")
    customer: Mapped[Customer] = relationship("Customer")
    lines: Mapped[list["DeliveryLine"]] = relationship(
        "DeliveryLine",
        back_populates="delivery",
        cascade="all, delete-orphan",
    )


class DeliveryLine(Base):
    """Line item in a Delivery document with COGS snapshot."""
    __tablename__ = "delivery_lines"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    delivery_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    so_line_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sales_order_lines.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost_snapshot: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)  # COGS snapshot

    delivery: Mapped[Delivery] = relationship(
        "Delivery", back_populates="lines")
    product: Mapped[Product] = relationship("Product")
    so_line: Mapped[SalesOrderLine] = relationship("SalesOrderLine")
