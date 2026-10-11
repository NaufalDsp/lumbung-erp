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

from app.domain.enums import PurchaseOrderStatus
from app.models.base import Base, TimestampMixin
from app.models.master import Product, Supplier


class PurchaseOrder(Base, TimestampMixin):
    """Purchase Order (PO) document entity."""
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str | None] = mapped_column(
        String(50), unique=True, index=True, nullable=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default=PurchaseOrderStatus.DRAF.value,
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    supplier: Mapped[Supplier] = relationship("Supplier")
    lines: Mapped[list["PurchaseOrderLine"]] = relationship(
        "PurchaseOrderLine",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[list["GoodsReceipt"]] = relationship(
        "GoodsReceipt",
        back_populates="purchase_order",
    )


class PurchaseOrderLine(Base):
    """Line item in a Purchase Order."""
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    received_qty: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    purchase_order: Mapped[PurchaseOrder] = relationship(
        "PurchaseOrder", back_populates="lines")
    product: Mapped[Product] = relationship("Product")


class GoodsReceipt(Base):
    """Goods Receipt (GR) document representing physical inventory intake."""
    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    po_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        "purchase_orders.id"), nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
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

    purchase_order: Mapped[PurchaseOrder] = relationship(
        "PurchaseOrder", back_populates="receipts")
    supplier: Mapped[Supplier] = relationship("Supplier")
    lines: Mapped[list["GoodsReceiptLine"]] = relationship(
        "GoodsReceiptLine",
        back_populates="goods_receipt",
        cascade="all, delete-orphan",
    )


class GoodsReceiptLine(Base):
    """Line item in a Goods Receipt document."""
    __tablename__ = "goods_receipt_lines"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    gr_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("goods_receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    po_line_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("purchase_order_lines.id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)

    goods_receipt: Mapped[GoodsReceipt] = relationship(
        "GoodsReceipt", back_populates="lines")
    product: Mapped[Product] = relationship("Product")
    po_line: Mapped[PurchaseOrderLine] = relationship("PurchaseOrderLine")
