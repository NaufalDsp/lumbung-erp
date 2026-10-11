from typing import Any


class DomainError(Exception):
    """Base exception for all domain business rule violations."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class StockInsufficientError(DomainError):
    """Raised when available stock is insufficient for confirmation or delivery."""

    def __init__(self, product_id: int, available: int, requested: int) -> None:
        super().__init__(
            code="STOK_TIDAK_CUKUP",
            message=f"Stok tersedia {available}, diminta {requested}",
            details={
                "product_id": product_id,
                "available": available,
                "requested": requested,
            },
        )


class InvalidStateTransitionError(DomainError):
    """Raised when an illegal document status transition is attempted."""

    def __init__(self, doc_type: str, current_status: str, target_status: str) -> None:
        super().__init__(
            code="TRANSISI_STATUS_TIDAK_SAH",
            message=f"Dokumen {doc_type} berstatus '{current_status}' tidak dapat berpindah ke '{target_status}'",
            details={
                "doc_type": doc_type,
                "current_status": current_status,
                "target_status": target_status,
            },
        )


class DocumentLockedError(DomainError):
    """Raised when attempting to edit a locked document (confirmed/issued)."""

    def __init__(self, doc_type: str, doc_number: str) -> None:
        super().__init__(
            code="DOKUMEN_DIKUNCI",
            message=f"Dokumen {doc_type} {doc_number} sudah terkunci dan tidak dapat diubah",
            details={
                "doc_type": doc_type,
                "doc_number": doc_number,
            },
        )


class InvalidAmountError(DomainError):
    """Raised when monetary or quantity value violates invariants."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="NILAI_TIDAK_VALID",
            message=message,
            details=details,
        )


class StockInvariantViolationError(DomainError):
    """Raised when stock ledger or balances invariant is broken."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="PELANGGARAN_INVARIAN_STOK",
            message=message,
            details=details,
        )
