from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import (
    DocType,
    PurchaseOrderStatus,
    StockAdjustmentReason,
    StockMoveKind,
)
from app.domain.exceptions import DomainError, InvalidStateTransitionError
from app.domain.stock_rules import (
    calculate_moving_average_cost,
    validate_stock_invariants,
)
from app.domain.values import DocNumber
from app.models.doc_sequence import DocSequence
from app.models.master import Product
from app.models.purchasing import (
    GoodsReceipt,
    GoodsReceiptLine,
    PurchaseOrder,
    PurchaseOrderLine,
)
from app.models.stock import StockBalance, StockMove
from app.services.audit import record_audit_log


async def get_next_doc_number(
    db: AsyncSession,
    doc_type: DocType,
    year: int | None = None,
) -> str:
    """Generates a sequential document number using row locking (SELECT ... FOR UPDATE).

    Guarantees no gaps and no duplicate numbers even under high concurrency.
    Format: {JENIS}-{TAHUN}-{URUT:06d}
    """
    current_year = year or datetime.now(timezone.utc).year
    type_str = doc_type.value

    # Lock sequence row for this document type and year
    stmt = (
        select(DocSequence)
        .where(DocSequence.doc_type == type_str, DocSequence.year == current_year)
        .with_for_update()
    )
    res = await db.execute(stmt)
    seq_record = res.scalar_one_or_none()

    if not seq_record:
        seq_record = DocSequence(
            doc_type=type_str, year=current_year, last_value=1)
        db.add(seq_record)
        next_seq = 1
    else:
        seq_record.last_value += 1
        next_seq = seq_record.last_value

    await db.flush()
    return DocNumber(doc_type=doc_type, year=current_year, sequence=next_seq).formatted()


async def process_goods_receipt(
    db: AsyncSession,
    po_id: int,
    receipt_lines: list[dict[str, int]],
    notes: str | None,
    user_id: int,
) -> GoodsReceipt:
    """Processes goods receipt against a Purchase Order in a single atomic transaction:

    1. Locks PO and verifies it is in DIPESAN or SEBAGIAN_DITERIMA status.
    2. Sorts product_ids ascending and locks stock_balances with SELECT ... FOR UPDATE (avoids deadlocks).
    3. Updates received_qty on PO lines.
    4. Appends to stock_moves (ledger).
    5. Updates moving average unit cost and on_hand balance.
    6. Updates PO status to SEBAGIAN_DITERIMA or DITERIMA.
    """
    stmt = (
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.lines))
        .where(PurchaseOrder.id == po_id)
        .with_for_update()
    )
    po = (await db.execute(stmt)).scalar_one_or_none()

    if not po:
        raise DomainError("PO_TIDAK_DITEMUKAN",
                          f"Pesanan pembelian ID {po_id} tidak ditemukan")

    if po.status not in (PurchaseOrderStatus.DIPESAN.value, PurchaseOrderStatus.SEBAGIAN_DITERIMA.value):
        raise InvalidStateTransitionError(
            DocType.PO.value, po.status, "penerimaan_barang")

    # Map lines by po_line_id
    po_lines_map = {line.id: line for line in po.lines}
    validated_items: list[tuple[PurchaseOrderLine, int]] = []
    product_ids_set: set[int] = set()

    for item in receipt_lines:
        line_id = item["po_line_id"]
        qty = item["qty"]

        if line_id not in po_lines_map:
            raise DomainError("BARIS_PO_TIDAK_VALID",
                              f"Baris PO {line_id} tidak ditemukan pada PO ini")

        po_line = po_lines_map[line_id]
        remaining = po_line.qty - po_line.received_qty

        if qty <= 0:
            raise DomainError("KUANTITAS_TIDAK_VALID",
                              f"Kuantitas penerimaan harus > 0 (diberikan {qty})")

        if qty > remaining:
            raise DomainError(
                "PENERIMAAN_MELEBIHI_PESANAN",
                f"Kuantitas penerimaan ({qty}) melebihi sisa pesanan ({remaining}) untuk produk {po_line.product_id}",
            )

        validated_items.append((po_line, qty))
        product_ids_set.add(po_line.product_id)

    # Lock stock balances in consistent ascending order to prevent deadlocks
    sorted_product_ids = sorted(product_ids_set)
    bal_stmt = (
        select(StockBalance)
        .where(StockBalance.product_id.in_(sorted_product_ids), StockBalance.warehouse_id == 1)
        .order_by(StockBalance.product_id.asc())
        .with_for_update()
    )
    bal_res = await db.execute(bal_stmt)
    balances_map = {b.product_id: b for b in bal_res.scalars().all()}

    # Create Goods Receipt document
    gr_number = await get_next_doc_number(db, DocType.GR)
    gr = GoodsReceipt(
        number=gr_number,
        po_id=po.id,
        supplier_id=po.supplier_id,
        notes=notes,
        created_by=user_id,
    )
    db.add(gr)
    await db.flush()

    for po_line, qty in validated_items:
        # Create GR Line
        gr_line = GoodsReceiptLine(
            gr_id=gr.id,
            po_line_id=po_line.id,
            product_id=po_line.product_id,
            qty=qty,
            unit_cost=po_line.unit_cost,
        )
        db.add(gr_line)

        # Update PO Line
        po_line.received_qty += qty

        # Update Balance & Moving Average Unit Cost
        bal = balances_map.get(po_line.product_id)
        if not bal:
            bal = StockBalance(
                product_id=po_line.product_id,
                warehouse_id=1,
                on_hand=0,
                reserved=0,
                avg_cost=po_line.unit_cost,
            )
            db.add(bal)
            balances_map[po_line.product_id] = bal

        new_avg_cost = calculate_moving_average_cost(
            old_qty=bal.on_hand,
            old_avg_cost=bal.avg_cost,
            received_qty=qty,
            unit_cost=po_line.unit_cost,
        )
        bal.on_hand += qty
        bal.avg_cost = new_avg_cost

        # Update master Product last_buy_price
        prod_stmt = select(Product).where(Product.id == po_line.product_id)
        prod = (await db.execute(prod_stmt)).scalar_one_or_none()
        if prod:
            prod.last_buy_price = po_line.unit_cost

        # Append to stock_moves (ledger)
        stock_move = StockMove(
            product_id=po_line.product_id,
            warehouse_id=1,
            qty=qty,
            kind=StockMoveKind.PENERIMAAN.value,
            doc_type=DocType.GR.value,
            doc_id=gr.id,
            unit_cost=po_line.unit_cost,
            created_by=user_id,
        )
        db.add(stock_move)

    # Determine new PO status
    all_received = all(line.received_qty >= line.qty for line in po.lines)
    old_status = po.status
    po.status = (
        PurchaseOrderStatus.DITERIMA.value
        if all_received
        else PurchaseOrderStatus.SEBAGIAN_DITERIMA.value
    )

    await record_audit_log(
        db=db,
        entity="purchase_order",
        entity_id=po.id,
        action="receive_goods",
        actor_id=user_id,
        from_status=old_status,
        to_status=po.status,
        diff={"gr_id": gr.id, "gr_number": gr.number},
    )

    await db.commit()
    return gr


async def record_stock_adjustment(
    db: AsyncSession,
    product_id: int,
    qty_change: int,
    reason: StockAdjustmentReason,
    notes: str,
    user_id: int,
) -> StockMove:
    """Executes a stock adjustment with reason and audit log."""
    if qty_change == 0:
        raise DomainError("KUANTITAS_TIDAK_VALID",
                          "Perubahan kuantitas tidak boleh 0")

    # Lock stock balance
    bal_stmt = (
        select(StockBalance)
        .where(StockBalance.product_id == product_id, StockBalance.warehouse_id == 1)
        .with_for_update()
    )
    bal = (await db.execute(bal_stmt)).scalar_one_or_none()
    if not bal:
        bal = StockBalance(product_id=product_id, warehouse_id=1,
                           on_hand=0, reserved=0, avg_cost=0)
        db.add(bal)
        await db.flush()

    new_on_hand = bal.on_hand + qty_change
    validate_stock_invariants(on_hand=new_on_hand, reserved=bal.reserved)

    bal.on_hand = new_on_hand

    # Append to stock_moves (ledger)
    move = StockMove(
        product_id=product_id,
        warehouse_id=1,
        qty=qty_change,
        kind=StockMoveKind.PENYESUAIAN.value,
        doc_type="ADJ",
        doc_id=0,
        unit_cost=bal.avg_cost,
        created_by=user_id,
    )
    db.add(move)
    await db.flush()

    await record_audit_log(
        db=db,
        entity="stock_balance",
        entity_id=product_id,
        action="adjust",
        actor_id=user_id,
        diff={
            "qty_change": qty_change,
            "new_on_hand": new_on_hand,
            "reason": reason.value,
            "notes": notes,
        },
    )

    await db.commit()
    return move


async def check_inventory_consistency(db: AsyncSession) -> list[dict[str, Any]]:
    """Consistency checker verifying on_hand == SUM(stock_moves.qty) per product."""
    # Group moves sum
    move_stmt = select(
        StockMove.product_id,
        func.sum(StockMove.qty).label("ledger_total"),
    ).group_by(StockMove.product_id)
    moves_res = await db.execute(move_stmt)
    moves_map = {row.product_id: (row.ledger_total or 0)
                 for row in moves_res.all()}

    # Query balances
    bal_stmt = select(StockBalance).where(StockBalance.warehouse_id == 1)
    bal_res = await db.execute(bal_stmt)
    balances = bal_res.scalars().all()

    discrepancies: list[dict[str, Any]] = []
    for b in balances:
        ledger_qty = moves_map.get(b.product_id, 0)
        if b.on_hand != ledger_qty:
            discrepancies.append({
                "product_id": b.product_id,
                "balance_on_hand": b.on_hand,
                "ledger_sum": ledger_qty,
                "difference": b.on_hand - ledger_qty,
            })

    return discrepancies
