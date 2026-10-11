from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StockMove(Base):
    """Append-only stock transaction ledger.

    Invariants: Records are never updated or deleted.
    """
    __tablename__ = "stock_moves"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, index=True)
    # positive for in, negative for out
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    # penerimaan, pengiriman, penyesuaian, koreksi
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    doc_type: Mapped[str] = mapped_column(
        String(10), nullable=False)  # PO, GR, SO, DO, INV, ADJ
    doc_id: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_stock_moves_product_created", "product_id", "created_at"),
    )


class StockBalance(Base):
    """Current on_hand, reserved, and moving average unit cost per product and warehouse.

    Hard constraints prevent negative inventory or over-reservation.
    """
    __tablename__ = "stock_balances"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, default=1)
    on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_cost: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("on_hand >= 0", name="chk_on_hand_nonneg"),
        CheckConstraint("reserved >= 0", name="chk_reserved_nonneg"),
        CheckConstraint("reserved <= on_hand", name="chk_reserved_le_hand"),
    )

    @property
    def available(self) -> int:
        return self.on_hand - self.reserved
