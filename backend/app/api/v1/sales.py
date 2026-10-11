from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.master import PaginatedResponse
from app.api.v1.schemas.sales import (
    DeliveryCreate,
    DeliveryLineResponse,
    DeliveryResponse,
    SalesOrderCreate,
    SalesOrderLineResponse,
    SalesOrderResponse,
    SalesOrderUpdate,
)
from app.core.permissions import Permission
from app.domain.enums import SalesOrderStatus
from app.domain.values import BasisPoints, Money
from app.models.database import get_db
from app.models.master import Customer, Product
from app.models.sales import (
    Delivery,
    DeliveryLine,
    SalesOrder,
    SalesOrderLine,
)
from app.services.audit import record_audit_log
from app.services.sales import (
    cancel_sales_order,
    confirm_sales_order,
    process_delivery_order,
)

router = APIRouter(tags=["Sales & Delivery"])


def _map_so_response(so: SalesOrder) -> SalesOrderResponse:
    lines: list[SalesOrderLineResponse] = []
    total_gross = 0
    total_discount = 0

    for line in so.lines:
        gross = line.qty * line.unit_price
        bp = BasisPoints(line.discount_bp)
        discount = bp.calculate_amount(Money(gross)).amount
        subtotal = gross - discount

        total_gross += gross
        total_discount += discount

        lines.append(
            SalesOrderLineResponse(
                id=line.id,
                so_id=line.so_id,
                product_id=line.product_id,
                product_name=line.product.name if line.product else None,
                product_sku=line.product.sku if line.product else None,
                qty=line.qty,
                unit_price=line.unit_price,
                discount_bp=line.discount_bp,
                delivered_qty=line.delivered_qty,
                gross_amount=gross,
                discount_amount=discount,
                subtotal=subtotal,
            )
        )

    return SalesOrderResponse(
        id=so.id,
        number=so.number,
        customer_id=so.customer_id,
        customer_name=so.customer.name if so.customer else None,
        status=so.status,
        notes=so.notes,
        ordered_at=so.ordered_at,
        total_gross=total_gross,
        total_discount=total_discount,
        total_amount=total_gross - total_discount,
        lines=lines,
    )


@router.get("/sales-orders", response_model=PaginatedResponse[SalesOrderResponse])
async def list_sales_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    status_filter: str | None = Query(None, alias="status"),
    customer_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[SalesOrderResponse]:
    stmt = (
        select(SalesOrder)
        .options(
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.lines).selectinload(
                SalesOrderLine.product),
        )
    )
    count_stmt = select(func.count(SalesOrder.id))

    if status_filter:
        stmt = stmt.where(SalesOrder.status == status_filter)
        count_stmt = count_stmt.where(SalesOrder.status == status_filter)

    if customer_id:
        stmt = stmt.where(SalesOrder.customer_id == customer_id)
        count_stmt = count_stmt.where(SalesOrder.customer_id == customer_id)

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    stmt = stmt.order_by(SalesOrder.id.desc()).offset(offset).limit(limit)

    res = await db.execute(stmt)
    orders = res.scalars().all()
    items = [_map_so_response(so) for so in orders]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/sales-orders/{so_id}", response_model=SalesOrderResponse)
async def get_sales_order(
    so_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> SalesOrderResponse:
    stmt = (
        select(SalesOrder)
        .options(
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.lines).selectinload(
                SalesOrderLine.product),
        )
        .where(SalesOrder.id == so_id)
    )
    res = await db.execute(stmt)
    so = res.scalar_one_or_none()
    if not so:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SO_TIDAK_DITEMUKAN",
                              "message": "Pesanan penjualan tidak ditemukan"}},
        )
    return _map_so_response(so)


@router.post("/sales-orders", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    payload: SalesOrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.SALES_CREATE_CONFIRM))],
) -> SalesOrderResponse:
    cust = (await db.execute(select(Customer).where(Customer.id == payload.customer_id))).scalar_one_or_none()
    if not cust:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PELANGGAN_TIDAK_DITEMUKAN",
                              "message": "Pelanggan tidak ditemukan"}},
        )

    so = SalesOrder(
        customer_id=payload.customer_id,
        notes=payload.notes,
        status=SalesOrderStatus.DRAF.value,
        created_by=current_user.id,
    )
    db.add(so)
    await db.flush()

    for line in payload.lines:
        so_line = SalesOrderLine(
            so_id=so.id,
            product_id=line.product_id,
            qty=line.qty,
            unit_price=line.unit_price,
            discount_bp=line.discount_bp,
        )
        db.add(so_line)

    await record_audit_log(
        db=db,
        entity="sales_order",
        entity_id=so.id,
        action="create_draft",
        actor_id=current_user.id,
        from_status=None,
        to_status=so.status,
    )
    await db.commit()

    return await get_sales_order(so.id, db, current_user)


@router.post("/sales-orders/{so_id}/confirm", response_model=SalesOrderResponse)
async def confirm_sales_order_endpoint(
    so_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.SALES_CREATE_CONFIRM))],
) -> SalesOrderResponse:
    """Confirms Sales Order, checks availability, reserves inventory, and issues document number."""
    try:
        await confirm_sales_order(db=db, so_id=so_id, user_id=current_user.id)
    except Exception as e:
        error_code = getattr(e, "code", "GALAT_KONFIRMASI_SO")
        details = getattr(e, "details", None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": error_code,
                              "message": str(e), "details": details}},
        )

    return await get_sales_order(so_id, db, current_user)


@router.post("/sales-orders/{so_id}/cancel", response_model=SalesOrderResponse)
async def cancel_sales_order_endpoint(
    so_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.SALES_CREATE_CONFIRM))],
) -> SalesOrderResponse:
    """Cancels Sales Order and releases inventory reservations if eligible."""
    try:
        await cancel_sales_order(db=db, so_id=so_id, user_id=current_user.id)
    except Exception as e:
        error_code = getattr(e, "code", "GALAT_BATAL_SO")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": error_code, "message": str(e)}},
        )

    return await get_sales_order(so_id, db, current_user)


@router.post("/deliveries", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_order(
    payload: DeliveryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.STOCK_DELIVER_GOODS))],
) -> DeliveryResponse:
    """Processes shipment (DO), decreases on_hand & reserved, captures COGS snapshot, and writes to ledger."""
    lines_data = [item.model_dump() for item in payload.lines]
    try:
        deliv = await process_delivery_order(
            db=db,
            so_id=payload.so_id,
            lines_data=lines_data,
            notes=payload.notes,
            user_id=current_user.id,
        )
    except Exception as e:
        error_code = getattr(e, "code", "GALAT_PENGIRIMAN")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": error_code, "message": str(e)}},
        )

    # Requery with relationships
    stmt = (
        select(Delivery)
        .options(
            selectinload(Delivery.customer),
            selectinload(Delivery.lines).selectinload(DeliveryLine.product),
        )
        .where(Delivery.id == deliv.id)
    )
    full_deliv = (await db.execute(stmt)).scalar_one()

    return DeliveryResponse(
        id=full_deliv.id,
        number=full_deliv.number,
        so_id=full_deliv.so_id,
        customer_id=full_deliv.customer_id,
        customer_name=full_deliv.customer.name if full_deliv.customer else None,
        notes=full_deliv.notes,
        delivered_at=full_deliv.delivered_at,
        lines=[
            DeliveryLineResponse(
                id=line.id,
                delivery_id=line.delivery_id,
                so_line_id=line.so_line_id,
                product_id=line.product_id,
                product_name=line.product.name if line.product else None,
                product_sku=line.product.sku if line.product else None,
                qty=line.qty,
                unit_cost_snapshot=line.unit_cost_snapshot,
            )
            for line in full_deliv.lines
        ],
    )


@router.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> DeliveryResponse:
    stmt = (
        select(Delivery)
        .options(
            selectinload(Delivery.customer),
            selectinload(Delivery.lines).selectinload(DeliveryLine.product),
        )
        .where(Delivery.id == delivery_id)
    )
    res = await db.execute(stmt)
    deliv = res.scalar_one_or_none()
    if not deliv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PENGIRIMAN_TIDAK_DITEMUKAN",
                              "message": "Surat jalan tidak ditemukan"}},
        )

    return DeliveryResponse(
        id=deliv.id,
        number=deliv.number,
        so_id=deliv.so_id,
        customer_id=deliv.customer_id,
        customer_name=deliv.customer.name if deliv.customer else None,
        notes=deliv.notes,
        delivered_at=deliv.delivered_at,
        lines=[
            DeliveryLineResponse(
                id=line.id,
                delivery_id=line.delivery_id,
                so_line_id=line.so_line_id,
                product_id=line.product_id,
                product_name=line.product.name if line.product else None,
                product_sku=line.product.sku if line.product else None,
                qty=line.qty,
                unit_cost_snapshot=line.unit_cost_snapshot,
            )
            for line in deliv.lines
        ],
    )
