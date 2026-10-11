from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

from app.domain.enums import DocType
from app.domain.exceptions import InvalidAmountError


@dataclass(frozen=True, slots=True)
class Money:
    """Value object representing Indonesian Rupiah stored as pure integer (BIGINT).

    Zero floating point drift.
    """
    amount: int

    def __add__(self, other: Self | int) -> Money:
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        if isinstance(other, int):
            return Money(self.amount + other)
        return NotImplemented

    def __sub__(self, other: Self | int) -> Money:
        if isinstance(other, Money):
            return Money(self.amount - other.amount)
        if isinstance(other, int):
            return Money(self.amount - other)
        return NotImplemented

    def __mul__(self, factor: int) -> Money:
        if not isinstance(factor, int):
            raise InvalidAmountError(
                "Faktor pengali uang harus bilangan bulat")
        return Money(self.amount * factor)

    def __lt__(self, other: Self) -> bool:
        return self.amount < other.amount

    def __le__(self, other: Self) -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: Self) -> bool:
        return self.amount > other.amount

    def __ge__(self, other: Self) -> bool:
        return self.amount >= other.amount

    def __str__(self) -> str:
        return self.format_idr()

    def format_idr(self) -> str:
        """Format to 'Rp 1.250.000' or '-Rp 450.000' with dot thousand separators."""
        is_negative = self.amount < 0
        abs_val = abs(self.amount)
        formatted_number = f"{abs_val:,}".replace(",", ".")
        if is_negative:
            return f"-Rp {formatted_number}"
        return f"Rp {formatted_number}"

    @classmethod
    def zero(cls) -> Money:
        return cls(0)


@dataclass(frozen=True, slots=True)
class BasisPoints:
    """Value object representing percentage in basis points (1 bp = 0.01%).

    Example: 1100 bp = 11.00% (PPN 11%).
    Rounding uses standard integer half-up rounding.
    """
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidAmountError(
                "Basis points tidak boleh bernilai negatif")

    def calculate_amount(self, base: Money) -> Money:
        """Calculate amount = (base * bp + 5000) // 10000 with half-up rounding."""
        if base.amount == 0 or self.value == 0:
            return Money.zero()

        # Standard half-up integer rounding: (X + 5000) // 10000
        sign = 1 if base.amount >= 0 else -1
        abs_base = abs(base.amount)
        rounded = (abs_base * self.value + 5000) // 10000
        return Money(sign * rounded)

    @classmethod
    def from_percent(cls, percent: int) -> BasisPoints:
        return cls(percent * 100)

    @classmethod
    def ppn_default(cls) -> BasisPoints:
        return cls(1100)  # 11%


_DOC_NUMBER_PATTERN = re.compile(r"^([A-Z]{2,3})-(\d{4})-(\d{6})$")


@dataclass(frozen=True, slots=True)
class DocNumber:
    """Value object for document numbers following {JENIS}-{TAHUN}-{URUT 6 digit} format.

    Example: SO-2026-000042, INV-2026-000017.
    """
    doc_type: DocType
    year: int
    sequence: int

    def __post_init__(self) -> None:
        if self.year < 2000 or self.year > 2100:
            raise InvalidAmountError(f"Tahun dokumen tidak valid: {self.year}")
        if self.sequence < 1 or self.sequence > 999999:
            raise InvalidAmountError(
                f"Nomor urut dokumen harus antara 1-999999: {self.sequence}")

    def formatted(self) -> str:
        return f"{self.doc_type.value}-{self.year}-{self.sequence:06d}"

    def __str__(self) -> str:
        return self.formatted()

    @classmethod
    def parse(cls, value: str) -> DocNumber:
        match = _DOC_NUMBER_PATTERN.match(value.strip())
        if not match:
            raise InvalidAmountError(
                f"Format nomor dokumen tidak valid: '{value}'. Format harus JENIS-YYYY-000000")

        raw_type, raw_year, raw_seq = match.groups()
        try:
            doc_type = DocType(raw_type)
        except ValueError:
            raise InvalidAmountError(
                f"Jenis dokumen tidak dikenal: {raw_type}")

        return cls(
            doc_type=doc_type,
            year=int(raw_year),
            sequence=int(raw_seq),
        )
