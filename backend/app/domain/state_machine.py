from app.domain.enums import (
    DocType,
    InvoiceStatus,
    PurchaseOrderStatus,
    SalesOrderStatus,
)
from app.domain.exceptions import InvalidStateTransitionError


class SalesOrderStateMachine:
    """State machine governing Sales Order (SO) status transitions."""

    _ALLOWED_TRANSITIONS: dict[SalesOrderStatus, set[SalesOrderStatus]] = {
        SalesOrderStatus.DRAF: {
            SalesOrderStatus.DIKONFIRMASI,
            SalesOrderStatus.BATAL,
        },
        SalesOrderStatus.DIKONFIRMASI: {
            SalesOrderStatus.SEBAGIAN_TERKIRIM,
            SalesOrderStatus.TERKIRIM,
            SalesOrderStatus.BATAL,
        },
        SalesOrderStatus.SEBAGIAN_TERKIRIM: {
            SalesOrderStatus.TERKIRIM,
        },
        SalesOrderStatus.TERKIRIM: {
            SalesOrderStatus.SELESAI,
        },
        SalesOrderStatus.SELESAI: set(),
        SalesOrderStatus.BATAL: set(),
    }

    @classmethod
    def can_transition(cls, current: SalesOrderStatus, target: SalesOrderStatus) -> bool:
        return target in cls._ALLOWED_TRANSITIONS.get(current, set())

    @classmethod
    def validate_transition(
        cls,
        current: SalesOrderStatus,
        target: SalesOrderStatus,
        has_deliveries: bool = False,
    ) -> None:
        """Validate transition.

        Special invariant: SO can only be cancelled from DIKONFIRMASI if no deliveries exist.
        """
        if not cls.can_transition(current, target):
            raise InvalidStateTransitionError(
                doc_type=DocType.SO.value,
                current_status=current.value,
                target_status=target.value,
            )

        if target == SalesOrderStatus.BATAL and has_deliveries:
            raise InvalidStateTransitionError(
                doc_type=DocType.SO.value,
                current_status=current.value,
                target_status=target.value,
            )


class PurchaseOrderStateMachine:
    """State machine governing Purchase Order (PO) status transitions."""

    _ALLOWED_TRANSITIONS: dict[PurchaseOrderStatus, set[PurchaseOrderStatus]] = {
        PurchaseOrderStatus.DRAF: {
            PurchaseOrderStatus.DIPESAN,
            PurchaseOrderStatus.BATAL,
        },
        PurchaseOrderStatus.DIPESAN: {
            PurchaseOrderStatus.SEBAGIAN_DITERIMA,
            PurchaseOrderStatus.DITERIMA,
            PurchaseOrderStatus.BATAL,
        },
        PurchaseOrderStatus.SEBAGIAN_DITERIMA: {
            PurchaseOrderStatus.DITERIMA,
        },
        PurchaseOrderStatus.DITERIMA: set(),
        PurchaseOrderStatus.BATAL: set(),
    }

    @classmethod
    def can_transition(cls, current: PurchaseOrderStatus, target: PurchaseOrderStatus) -> bool:
        return target in cls._ALLOWED_TRANSITIONS.get(current, set())

    @classmethod
    def validate_transition(
        cls,
        current: PurchaseOrderStatus,
        target: PurchaseOrderStatus,
        has_receipts: bool = False,
    ) -> None:
        if not cls.can_transition(current, target):
            raise InvalidStateTransitionError(
                doc_type=DocType.PO.value,
                current_status=current.value,
                target_status=target.value,
            )

        if target == PurchaseOrderStatus.BATAL and has_receipts:
            raise InvalidStateTransitionError(
                doc_type=DocType.PO.value,
                current_status=current.value,
                target_status=target.value,
            )


class InvoiceStateMachine:
    """State machine governing Invoice (INV) status transitions."""

    _ALLOWED_TRANSITIONS: dict[InvoiceStatus, set[InvoiceStatus]] = {
        InvoiceStatus.DRAF: {
            InvoiceStatus.TERBIT,
        },
        InvoiceStatus.TERBIT: {
            InvoiceStatus.SEBAGIAN_DIBAYAR,
            InvoiceStatus.LUNAS,
            InvoiceStatus.VOID,
        },
        InvoiceStatus.SEBAGIAN_DIBAYAR: {
            InvoiceStatus.LUNAS,
        },
        InvoiceStatus.LUNAS: set(),
        InvoiceStatus.VOID: set(),
    }

    @classmethod
    def can_transition(cls, current: InvoiceStatus, target: InvoiceStatus) -> bool:
        return target in cls._ALLOWED_TRANSITIONS.get(current, set())

    @classmethod
    def validate_transition(
        cls,
        current: InvoiceStatus,
        target: InvoiceStatus,
        has_payments: bool = False,
    ) -> None:
        if not cls.can_transition(current, target):
            raise InvalidStateTransitionError(
                doc_type=DocType.INV.value,
                current_status=current.value,
                target_status=target.value,
            )

        if target == InvoiceStatus.VOID and has_payments:
            raise InvalidStateTransitionError(
                doc_type=DocType.INV.value,
                current_status=current.value,
                target_status=target.value,
            )
