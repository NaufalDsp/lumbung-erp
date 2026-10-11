from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Product category hierarchy."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category")


class Product(Base, TimestampMixin):
    """Inventory item master with standardized SKU and integer pricing."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True)
    unit: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pcs")  # pcs, sak, kg, batang, dus
    sell_price: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    last_buy_price: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)

    category: Mapped[Category | None] = relationship(
        "Category", back_populates="products")

    __table_args__ = (
        Index("ix_products_name_sku", "name", "sku"),
    )


class Customer(Base, TimestampMixin):
    """Customer entity with payment terms and credit limit."""
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    terms_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30)  # 0 (cash), 14, 30 days
    credit_limit: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)


class Supplier(Base, TimestampMixin):
    """Vendor / Supplier master entity."""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
