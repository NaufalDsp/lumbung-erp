from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.master import PaginatedResponse
from app.api.v1.schemas.stock import (
    StockAdjustmentCreate,
    StockBalanceResponse,
    StockConsistencyReport,
    StockMoveResponse,
)
from app.core.permissions import Permission
from app.models.database import get_db
from app.models.master import Product
from app.models.stock import StockBalance, StockMove
from app.services.stock import (
    check_inventory_consistency,
    record_stock_adjustment,
)

router = APIRouter(prefix="/stock", tags=["Stock & Inventory"])


@router.get("/balances", response_model=PaginatedResponse[StockBalanceResponse])
async def list_stock_balances(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    q: str | None = Query(None, description="Pencarian SKU atau nama produk"),
    below_min: bool | None = Query(
        None, description="Hanya tampilkan produk di bawah stok minimum"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> PaginatedResponse[StockBalanceResponse]:
    """Retrieves current on_hand, reserved, available, and moving average unit cost."""
    stmt = (
        select(StockBalance, Product)
        .join(Product, StockBalance.product_id == Product.id)
        .options(selectinload(Product.category))
        .where(StockBalance.warehouse_id == 1)
    )
    count_stmt = (
        select(func.count(StockBalance.product_id))
        .join(Product, StockBalance.product_id == Product.id)
        .where(StockBalance.warehouse_id == 1)
    )

    if q:
        search = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.sku.ilike(
            search), Product.name.ilike(search)))
        count_stmt = count_stmt.where(
            or_(Product.sku.ilike(search), Product.name.ilike(search)))

    if below_min:
        stmt = stmt.where(
            (StockBalance.on_hand - StockBalance.reserved) <= Product.min_stock)
        count_stmt = count_stmt.where(
            (StockBalance.on_hand - StockBalance.reserved) <= Product.min_stock)

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    stmt = stmt.order_by(Product.sku.asc()).offset(offset).limit(limit)

    res = await db.execute(stmt)
    rows = res.all()

    items = [
        StockBalanceResponse(
            product_id=prod.id,
            product_sku=prod.sku,
            product_name=prod.name,
            category_name=prod.category.name if prod.category else None,
            unit=prod.unit,
            on_hand=bal.on_hand,
            reserved=bal.reserved,
            available=bal.on_hand - bal.reserved,
            avg_cost=bal.avg_cost,
            total_value=bal.on_hand * bal.avg_cost,
        )
        for bal, prod in rows
    ]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/moves", response_model=PaginatedResponse[StockMoveResponse])
async def list_stock_moves(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    product_id: int | None = Query(
        None, description="Filter kartu stok produk tertentu"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> PaginatedResponse[StockMoveResponse]:
    """Stock movement ledger (kartu stok) ordered by newest first."""
    stmt = (
        select(StockMove, Product)
        .join(Product, StockMove.product_id == Product.id)
    )
    count_stmt = select(func.count(StockMove.id))

    if product_id is not None:
        stmt = stmt.where(StockMove.product_id == product_id)
        count_stmt = count_stmt.where(StockMove.product_id == product_id)

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    stmt = stmt.order_by(StockMove.created_at.desc(),
                         StockMove.id.desc()).offset(offset).limit(limit)

    res = await db.execute(stmt)
    rows = res.all()

    items = [
        StockMoveResponse(
            id=move.id,
            product_id=move.product_id,
            product_sku=prod.sku,
            product_name=prod.name,
            warehouse_id=move.warehouse_id,
            qty=move.qty,
            kind=move.kind,
            doc_type=move.doc_type,
            doc_id=move.doc_id,
            unit_cost=move.unit_cost,
            created_at=move.created_at,
        )
        for move, prod in rows
    ]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.post("/adjustments", response_model=StockMoveResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_adjustment(
    payload: StockAdjustmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.STOCK_ADJUST))],
) -> StockMoveResponse:
    """Adjusts stock on hand with mandatory reason and ledger entry."""
    prod = (await db.execute(select(Product).where(Product.id == payload.product_id))).scalar_one_or_none()
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PRODUK_TIDAK_DITEMUKAN",
                              "message": "Produk tidak ditemukan"}},
        )

    try:
        move = await record_stock_adjustment(
            db=db,
            product_id=payload.product_id,
            qty_change=payload.qty_change,
            reason=payload.reason,
            notes=payload.notes,
            user_id=current_user.id,
        )
    except Exception as e:
        error_code = getattr(e, "code", "GALAT_PENYESUAIAN_STOK")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": error_code, "message": str(e)}},
        )

    return StockMoveResponse(
        id=move.id,
        product_id=move.product_id,
        product_sku=prod.sku,
        product_name=prod.name,
        warehouse_id=move.warehouse_id,
        qty=move.qty,
        kind=move.kind,
        doc_type=move.doc_type,
        doc_id=move.doc_id,
        unit_cost=move.unit_cost,
        created_at=move.created_at,
    )


@router.get("/check-consistency", response_model=StockConsistencyReport)
async def verify_inventory_consistency(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> StockConsistencyReport:
    """Scheduled/Administrative check ensuring on_hand equals SUM(stock_moves)."""
    discrepancies = await check_inventory_consistency(db)
    return StockConsistencyReport(
        is_consistent=len(discrepancies) == 0,
        discrepancies=discrepancies,
    )
