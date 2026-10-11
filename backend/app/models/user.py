from sqlalchemy import Boolean, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Internal system user with role-based access control."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sales")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    google_sub: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True)

    __table_args__ = (
        Index("ix_users_role", "role"),
    )
