from datetime import datetime
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.reports import (
    ARAgingResponse,
    LowStockItem,
    SalesSummaryResponse,
    StockCardResponse,
    StockValuationResponse,
)
from app.core.permissions import Permission
from app.models.database import get_db
from app.models.user import User
from app.services.reports import (
    check_and_notify_low_stock,
    generate_csv,
    get_ar_aging_report,
    get_sales_summary_report,
    get_stock_card_report,
    get_stock_valuation_report,
)

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/stock-valuation", response_model=StockValuationResponse)
async def stock_valuation(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    return await get_stock_valuation_report(db)


@router.get("/stock-valuation/csv")
async def stock_valuation_csv(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    data = await get_stock_valuation_report(db)
    headers = [
        "SKU",
        "Nama Produk",
        "Kategori",
        "Satuan",
        "Stok Fisik",
        "Tereservasi",
        "Tersedia",
        "HPP Rata-rata (Rp)",
        "Total Nilai Aset (Rp)",
    ]
    rows = [
        [
            item["sku"],
            item["name"],
            item["category_name"],
            item["unit"],
            item["on_hand"],
            item["reserved"],
            item["available"],
            item["unit_cogs"],
            item["total_valuation"],
        ]
        for item in data["items"]
    ]
    csv_content = generate_csv(headers, rows)
    filename = f"nilai-persediaan-{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/sales-summary", response_model=SalesSummaryResponse)
async def sales_summary(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    return await get_sales_summary_report(db, start_date=start_date, end_date=end_date)


@router.get("/ar-aging", response_model=ARAgingResponse)
async def ar_aging(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    return await get_ar_aging_report(db)


@router.get("/ar-aging/csv")
async def ar_aging_csv(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    data = await get_ar_aging_report(db)
    headers = [
        "Pelanggan",
        "Lancar (Belum Jatuh Tempo)",
        "1-30 Hari",
        "31-60 Hari",
        "61-90 Hari",
        ">90 Hari",
        "Total Piutang (Rp)",
    ]
    rows = [
        [
            c["customer_name"],
            c["current"],
            c["days_1_30"],
            c["days_31_60"],
            c["days_61_90"],
            c["days_over_90"],
            c["total_unpaid"],
        ]
        for c in data["customers"]
    ]
    csv_content = generate_csv(headers, rows)
    filename = f"penuaan-piutang-{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/stock-card/{product_id}", response_model=StockCardResponse)
async def stock_card(
    product_id: int,
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    return await get_stock_card_report(db, product_id=product_id, limit=limit)


@router.get("/low-stock", response_model=list[LowStockItem])
async def list_low_stock(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.VIEW_INVENTORY_VALUATION_COGS)),
):
    return await check_and_notify_low_stock(db, send_telegram=False)


@router.post("/low-stock/trigger-alerts", response_model=list[LowStockItem])
async def trigger_low_stock_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.MANAGE_USERS_SETTINGS)),
):
    return await check_and_notify_low_stock(db, send_telegram=True)
