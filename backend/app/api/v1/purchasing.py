from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.master import PaginatedResponse
from app.api.v1.schemas.purchasing import (
    GoodsReceiptCreate,
    GoodsReceiptLineResponse,
    GoodsReceiptResponse,
    PurchaseOrderCreate,
    PurchaseOrderLineResponse,
    PurchaseOrderResponse,
    PurchaseOrderUpdate,
)
from app.core.permissions import Permission
from app.domain.enums import DocType, PurchaseOrderStatus
from app.domain.state_machine import PurchaseOrderStateMachine
from app.models.database import get_db
from app.models.master import Product, Supplier
from app.models.purchasing import (
    GoodsReceipt,
    PurchaseOrder,
    PurchaseOrderLine,
)
from app.services.audit import record_audit_log
from app.services.stock import get_next_doc_number, process_goods_receipt

router = APIRouter(tags=["Purchasing"])


def _map_po_response(po: PurchaseOrder) -> PurchaseOrderResponse:
    lines = [
        PurchaseOrderLineResponse(
            id=line.id,
            po_id=line.po_id,
            product_id=line.product_id,
            product_name=line.product.name if line.product else None,
            product_sku=line.product.sku if line.product else None,
            qty=line.qty,
            unit_cost=line.unit_cost,
            received_qty=line.received_qty,
            subtotal=line.qty * line.unit_cost,
        )
        for line in po.lines
    ]
    total_amount = sum(line.subtotal for line in lines)
    return PurchaseOrderResponse(
        id=po.id,
        number=po.number,
        supplier_id=po.supplier_id,
        supplier_name=po.supplier.name if po.supplier else None,
        status=po.status,
        notes=po.notes,
        ordered_at=po.ordered_at,
        total_amount=total_amount,
        lines=lines,
    )


@router.get("/purchase-orders", response_model=PaginatedResponse[PurchaseOrderResponse])
async def list_purchase_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    status_filter: str | None = Query(None, alias="status"),
    supplier_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[PurchaseOrderResponse]:
    stmt = (
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.lines).selectinload(
                PurchaseOrderLine.product),
        )
    )
    count_stmt = select(func.count(PurchaseOrder.id))

    if status_filter:
        stmt = stmt.where(PurchaseOrder.status == status_filter)
        count_stmt = count_stmt.where(PurchaseOrder.status == status_filter)

    if supplier_id:
        stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
        count_stmt = count_stmt.where(PurchaseOrder.supplier_id == supplier_id)

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    stmt = stmt.order_by(PurchaseOrder.id.desc()).offset(offset).limit(limit)

    res = await db.execute(stmt)
    orders = res.scalars().all()
    items = [_map_po_response(po) for po in orders]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> PurchaseOrderResponse:
    stmt = (
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.lines).selectinload(
                PurchaseOrderLine.product),
        )
        .where(PurchaseOrder.id == po_id)
    )
    res = await db.execute(stmt)
    po = res.scalar_one_or_none()
    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PO_TIDAK_DITEMUKAN",
                              "message": "Pesanan pembelian tidak ditemukan"}},
        )
    return _map_po_response(po)


@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.PURCHASE_CREATE_CONFIRM))],
) -> PurchaseOrderResponse:
    supp = (await db.execute(select(Supplier).where(Supplier.id == payload.supplier_id))).scalar_one_or_none()
    if not supp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PEMASOK_TIDAK_DITEMUKAN",
                              "message": "Pemasok tidak ditemukan"}},
        )

    po = PurchaseOrder(
        supplier_id=payload.supplier_id,
        notes=payload.notes,
        status=PurchaseOrderStatus.DRAF.value,
        created_by=current_user.id,
    )
    db.add(po)
    await db.flush()

    for line in payload.lines:
        po_line = PurchaseOrderLine(
            po_id=po.id,
            product_id=line.product_id,
            qty=line.qty,
            unit_cost=line.unit_cost,
        )
        db.add(po_line)

    await record_audit_log(
        db=db,
        entity="purchase_order",
        entity_id=po.id,
        action="create_draft",
        actor_id=current_user.id,
        from_status=None,
        to_status=po.status,
    )
    await db.commit()

    return await get_purchase_order(po.id, db, current_user)


@router.post("/purchase-orders/{po_id}/confirm", response_model=PurchaseOrderResponse)
async def confirm_purchase_order(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.PURCHASE_CREATE_CONFIRM))],
) -> PurchaseOrderResponse:
    stmt = (
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.lines))
        .where(PurchaseOrder.id == po_id)
        .with_for_update()
    )
    po = (await db.execute(stmt)).scalar_one_or_none()
    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PO_TIDAK_DITEMUKAN",
                              "message": "Pesanan pembelian tidak ditemukan"}},
        )

    PurchaseOrderStateMachine.validate_transition(
        current=PurchaseOrderStatus(po.status),
        target=PurchaseOrderStatus.DIPESAN,
    )

    if not po.lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "PO_KOSONG",
                              "message": "PO harus memiliki minimal satu baris barang"}},
        )

    # Issue sequential number
    po_number = await get_next_doc_number(db, DocType.PO)
    old_status = po.status
    po.number = po_number
    po.status = PurchaseOrderStatus.DIPESAN.value
    po.ordered_at = datetime.now(timezone.utc)

    await record_audit_log(
        db=db,
        entity="purchase_order",
        entity_id=po.id,
        action="confirm",
        actor_id=current_user.id,
        from_status=old_status,
        to_status=po.status,
        diff={"number": po_number},
    )
    await db.commit()
    return await get_purchase_order(po.id, db, current_user)


@router.post("/purchase-orders/{po_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_purchase_order(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.PURCHASE_CREATE_CONFIRM))],
) -> PurchaseOrderResponse:
    stmt = (
        select(PurchaseOrder)
        .options(selectinload(PurchaseOrder.lines))
        .where(PurchaseOrder.id == po_id)
        .with_for_update()
    )
    po = (await db.execute(stmt)).scalar_one_or_none()
    if not po:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PO_TIDAK_DITEMUKAN",
                              "message": "Pesanan pembelian tidak ditemukan"}},
        )

    has_receipts = any(line.received_qty > 0 for line in po.lines)
    PurchaseOrderStateMachine.validate_transition(
        current=PurchaseOrderStatus(po.status),
        target=PurchaseOrderStatus.BATAL,
        has_receipts=has_receipts,
    )

    old_status = po.status
    po.status = PurchaseOrderStatus.BATAL.value

    await record_audit_log(
        db=db,
        entity="purchase_order",
        entity_id=po.id,
        action="cancel",
        actor_id=current_user.id,
        from_status=old_status,
        to_status=po.status,
    )
    await db.commit()
    return await get_purchase_order(po.id, db, current_user)


@router.post("/goods-receipts", response_model=GoodsReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_goods_receipt(
    payload: GoodsReceiptCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.STOCK_RECEIVE_GOODS))],
) -> GoodsReceiptResponse:
    """Processes goods receipt against an active PO and writes to stock ledger."""
    lines_data = [item.model_dump() for item in payload.lines]
    try:
        gr = await process_goods_receipt(
            db=db,
            po_id=payload.po_id,
            receipt_lines=lines_data,
            notes=payload.notes,
            user_id=current_user.id,
        )
    except Exception as e:
        error_code = getattr(e, "code", "GALAT_PENERIMAAN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": error_code, "message": str(e)}},
        )

    # Requery with relationships
    stmt = (
        select(GoodsReceipt)
        .options(
            selectinload(GoodsReceipt.supplier),
            selectinload(GoodsReceipt.lines).selectinload(
                PurchaseOrderLine.product),
        )
        .where(GoodsReceipt.id == gr.id)
    )
    full_gr = (await db.execute(stmt)).scalar_one()

    return GoodsReceiptResponse(
        id=full_gr.id,
        number=full_gr.number,
        po_id=full_gr.po_id,
        supplier_id=full_gr.supplier_id,
        supplier_name=full_gr.supplier.name if full_gr.supplier else None,
        notes=full_gr.notes,
        received_at=full_gr.received_at,
        lines=[
            GoodsReceiptLineResponse(
                id=line.id,
                gr_id=line.gr_id,
                po_line_id=line.po_line_id,
                product_id=line.product_id,
                product_name=line.product.name if line.product else None,
                product_sku=line.product.sku if line.product else None,
                qty=line.qty,
                unit_cost=line.unit_cost,
            )
            for line in full_gr.lines
        ],
    )
