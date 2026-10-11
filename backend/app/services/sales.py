from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import DocType, SalesOrderStatus, StockMoveKind
from app.domain.exceptions import DomainError, StockInsufficientError
from app.domain.state_machine import SalesOrderStateMachine
from app.domain.stock_rules import validate_stock_invariants
from app.models.sales import (
    Delivery,
    DeliveryLine,
    SalesOrder,
    SalesOrderLine,
)
from app.models.stock import StockBalance, StockMove
from app.services.audit import record_audit_log
from app.services.stock import get_next_doc_number


async def confirm_sales_order(
    db: AsyncSession,
    so_id: int,
    user_id: int,
) -> SalesOrder:
    """Confirms a Sales Order:

    1. Validates status transition DRAF -> DIKONFIRMASI.
    2. Locks stock_balances in consistent ascending order (SELECT ... FOR UPDATE).
    3. Verifies available stock (on_hand - reserved >= requested).
    4. Increases reserved stock.
    5. Issues gapless sequential document number (SO-YYYY-XXXXXX).
    6. Locks pricing and records audit log.
    """
    stmt = (
        select(SalesOrder)
        .options(selectinload(SalesOrder.lines))
        .where(SalesOrder.id == so_id)
        .with_for_update()
    )
    so = (await db.execute(stmt)).scalar_one_or_none()
    if not so:
        raise DomainError("SO_TIDAK_DITEMUKAN",
                          f"Pesanan penjualan ID {so_id} tidak ditemukan")

    SalesOrderStateMachine.validate_transition(
        current=SalesOrderStatus(so.status),
        target=SalesOrderStatus.DIKONFIRMASI,
    )

    if not so.lines:
        raise DomainError(
            "SO_KOSONG", "Pesanan penjualan harus memiliki minimal satu baris barang")

    # Aggregate requested quantities per product
    req_qty_by_prod: dict[int, int] = {}
    for line in so.lines:
        req_qty_by_prod[line.product_id] = req_qty_by_prod.get(
            line.product_id, 0) + line.qty

    # Lock stock balances in ascending order to prevent deadlocks
    sorted_product_ids = sorted(req_qty_by_prod.keys())
    bal_stmt = (
        select(StockBalance)
        .where(StockBalance.product_id.in_(sorted_product_ids), StockBalance.warehouse_id == 1)
        .order_by(StockBalance.product_id.asc())
        .with_for_update()
    )
    bal_res = await db.execute(bal_stmt)
    balances_map = {b.product_id: b for b in bal_res.scalars().all()}

    # Verify stock availability for each product
    for prod_id, requested in req_qty_by_prod.items():
        bal = balances_map.get(prod_id)
        available = (bal.on_hand - bal.reserved) if bal else 0
        if available < requested:
            raise StockInsufficientError(
                product_id=prod_id,
                available=available,
                requested=requested,
            )

    # Reserve inventory
    for prod_id, requested in req_qty_by_prod.items():
        bal = balances_map[prod_id]
        bal.reserved += requested
        validate_stock_invariants(on_hand=bal.on_hand, reserved=bal.reserved)

    # Issue sequential SO number
    so_number = await get_next_doc_number(db, DocType.SO)
    old_status = so.status
    so.number = so_number
    so.status = SalesOrderStatus.DIKONFIRMASI.value
    so.ordered_at = datetime.now(timezone.utc)

    await record_audit_log(
        db=db,
        entity="sales_order",
        entity_id=so.id,
        action="confirm",
        actor_id=user_id,
        from_status=old_status,
        to_status=so.status,
        diff={"number": so_number, "reserved_items": req_qty_by_prod},
    )

    await db.commit()
    return so


async def cancel_sales_order(
    db: AsyncSession,
    so_id: int,
    user_id: int,
) -> SalesOrder:
    """Cancels a Sales Order and releases inventory reservations if previously confirmed."""
    stmt = (
        select(SalesOrder)
        .options(selectinload(SalesOrder.lines))
        .where(SalesOrder.id == so_id)
        .with_for_update()
    )
    so = (await db.execute(stmt)).scalar_one_or_none()
    if not so:
        raise DomainError("SO_TIDAK_DITEMUKAN",
                          f"Pesanan penjualan ID {so_id} tidak ditemukan")

    has_deliveries = any(line.delivered_qty > 0 for line in so.lines)
    SalesOrderStateMachine.validate_transition(
        current=SalesOrderStatus(so.status),
        target=SalesOrderStatus.BATAL,
        has_deliveries=has_deliveries,
    )

    # If was confirmed, release inventory reservations
    if so.status == SalesOrderStatus.DIKONFIRMASI.value:
        req_qty_by_prod: dict[int, int] = {}
        for line in so.lines:
            req_qty_by_prod[line.product_id] = req_qty_by_prod.get(
                line.product_id, 0) + line.qty

        sorted_product_ids = sorted(req_qty_by_prod.keys())
        bal_stmt = (
            select(StockBalance)
            .where(StockBalance.product_id.in_(sorted_product_ids), StockBalance.warehouse_id == 1)
            .order_by(StockBalance.product_id.asc())
            .with_for_update()
        )
        bal_res = await db.execute(bal_stmt)
        for bal in bal_res.scalars().all():
            qty_to_release = req_qty_by_prod.get(bal.product_id, 0)
            bal.reserved = max(0, bal.reserved - qty_to_release)

    old_status = so.status
    so.status = SalesOrderStatus.BATAL.value

    await record_audit_log(
        db=db,
        entity="sales_order",
        entity_id=so.id,
        action="cancel",
        actor_id=user_id,
        from_status=old_status,
        to_status=so.status,
    )

    await db.commit()
    return so


async def process_delivery_order(
    db: AsyncSession,
    so_id: int,
    lines_data: list[dict[str, int]],
    notes: str | None,
    user_id: int,
) -> Delivery:
    """Processes physical shipment (Delivery Order / Surat Jalan):

    1. Verifies SO is in DIKONFIRMASI or SEBAGIAN_TERKIRIM.
    2. Issues sequential DO-YYYY-XXXXXX number.
    3. Decreases on_hand and reserved simultaneously.
    4. Snapshots COGS from stock_balances.avg_cost.
    5. Appends outgoing movements to stock_moves.
    6. Updates SO status to SEBAGIAN_TERKIRIM or TERKIRIM.
    """
    stmt = (
        select(SalesOrder)
        .options(selectinload(SalesOrder.lines))
        .where(SalesOrder.id == so_id)
        .with_for_update()
    )
    so = (await db.execute(stmt)).scalar_one_or_none()
    if not so:
        raise DomainError("SO_TIDAK_DITEMUKAN",
                          f"Pesanan penjualan ID {so_id} tidak ditemukan")

    if so.status not in (SalesOrderStatus.DIKONFIRMASI.value, SalesOrderStatus.SEBAGIAN_TERKIRIM.value):
        raise DomainError(
            "STATUS_SO_TIDAK_VALID",
            f"Pengiriman hanya dapat dibuat dari SO berstatus Dikonfirmasi atau Sebagian Terkirim (saat ini: {so.status})",
        )

    so_lines_map = {line.id: line for line in so.lines}
    validated_items: list[tuple[SalesOrderLine, int]] = []
    product_ids_set: set[int] = set()

    for item in lines_data:
        so_line_id = item["so_line_id"]
        qty = item["qty"]

        if so_line_id not in so_lines_map:
            raise DomainError(
                "BARIS_SO_TIDAK_VALID", f"Baris SO {so_line_id} tidak ditemukan pada pesanan ini")

        so_line = so_lines_map[so_line_id]
        remaining = so_line.qty - so_line.delivered_qty

        if qty <= 0:
            raise DomainError("KUANTITAS_TIDAK_VALID",
                              f"Kuantitas pengiriman harus > 0 (diberikan {qty})")

        if qty > remaining:
            raise DomainError(
                "PENGIRIMAN_MELEBIHI_PESANAN",
                f"Kuantitas pengiriman ({qty}) melebihi sisa pesanan ({remaining}) untuk produk {so_line.product_id}",
            )

        validated_items.append((so_line, qty))
        product_ids_set.add(so_line.product_id)

    # Lock stock balances in ascending order
    sorted_product_ids = sorted(product_ids_set)
    bal_stmt = (
        select(StockBalance)
        .where(StockBalance.product_id.in_(sorted_product_ids), StockBalance.warehouse_id == 1)
        .order_by(StockBalance.product_id.asc())
        .with_for_update()
    )
    bal_res = await db.execute(bal_stmt)
    balances_map = {b.product_id: b for b in bal_res.scalars().all()}

    # Issue sequential DO number
    do_number = await get_next_doc_number(db, DocType.DO)
    delivery = Delivery(
        number=do_number,
        so_id=so.id,
        customer_id=so.customer_id,
        notes=notes,
        created_by=user_id,
    )
    db.add(delivery)
    await db.flush()

    for so_line, qty in validated_items:
        bal = balances_map.get(so_line.product_id)
        if not bal or bal.on_hand < qty or bal.reserved < qty:
            raise StockInsufficientError(
                product_id=so_line.product_id,
                available=bal.on_hand - bal.reserved if bal else 0,
                requested=qty,
            )

        cogs_snapshot = bal.avg_cost

        # Create Delivery Line
        deliv_line = DeliveryLine(
            delivery_id=delivery.id,
            so_line_id=so_line.id,
            product_id=so_line.product_id,
            qty=qty,
            unit_cost_snapshot=cogs_snapshot,
        )
        db.add(deliv_line)

        # Update SO line delivered_qty
        so_line.delivered_qty += qty

        # Decrease inventory: on_hand AND reserved decrease together
        bal.on_hand -= qty
        bal.reserved -= qty
        validate_stock_invariants(on_hand=bal.on_hand, reserved=bal.reserved)

        # Append to stock_moves (ledger)
        stock_move = StockMove(
            product_id=so_line.product_id,
            warehouse_id=1,
            qty=-qty,  # Negative for outgoing shipment
            kind=StockMoveKind.PENGIRIMAN.value,
            doc_type=DocType.DO.value,
            doc_id=delivery.id,
            unit_cost=cogs_snapshot,
            created_by=user_id,
        )
        db.add(stock_move)

    # Determine updated SO status
    all_delivered = all(line.delivered_qty >= line.qty for line in so.lines)
    old_status = so.status
    so.status = (
        SalesOrderStatus.TERKIRIM.value
        if all_delivered
        else SalesOrderStatus.SEBAGIAN_TERKIRIM.value
    )

    await record_audit_log(
        db=db,
        entity="sales_order",
        entity_id=so.id,
        action="deliver_goods",
        actor_id=user_id,
        from_status=old_status,
        to_status=so.status,
        diff={"delivery_id": delivery.id, "delivery_number": delivery.number},
    )

    await db.commit()
    return delivery
