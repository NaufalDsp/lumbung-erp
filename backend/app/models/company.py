from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    """Company settings and defaults. Single row table in v1."""
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, default="PT Lumbung Pangan Nusantara")
    address: Mapped[str] = mapped_column(
        Text, nullable=False, default="Kawasan Pergudangan Marunda Center Blok A3 No. 8, Jakarta Utara")
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="021-88997766")
    email: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default="kontak@lumbungpangan.co.id")
    tax_id_npwp: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="01.234.567.8-012.000")
    tax_rate_bp: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1100)  # 1100 = 11.00%
    default_terms_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30)
    invoice_footer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Pembayaran harap ditransfer ke BCA 1234567890 a/n PT Lumbung Pangan Nusantara",
    )
