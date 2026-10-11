from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocSequence(Base):
    """Tracks sequence numbers per document type and year to guarantee gapless, collision-free numbers.

    Locked with SELECT ... FOR UPDATE upon issuing.
    """
    __tablename__ = "doc_sequences"

    doc_type: Mapped[str] = mapped_column(String(10), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
