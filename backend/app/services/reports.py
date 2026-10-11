import csv
import io
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import InvoiceStatus, PaymentStatus
from app.integrations.notifications import get_telegram_notifier
from app.models.invoicing import Invoice, InvoiceLine, Payment
from app.models.master import Category, Customer, Product
from app.models.sales import Delivery, DeliveryLine
from app.models.stock import StockBalance, StockMove


async def get_stock_valuation_report(db: AsyncSession) -> dict[str, Any]:
    """Generates stock valuation report using Moving Average Cost."""
    stmt = (
        select(Product, StockBalance, Category.name.label("category_name"))
        .join(StockBalance, Product.id == StockBalance.product_id)
        .outerjoin(Category, Product.category_id == Category.id)
        .where(Product.is_active == True)
        .order_by(Product.name.asc())
    )
    results = (await db.execute(stmt)).all()

    items = []
    total_asset_value = 0
    total_units_on_hand = 0

    for prod, balance, cat_name in results:
        on_hand = balance.on_hand
        unit_cogs = prod.cogs_amount or 0
        valuation = on_hand * unit_cogs
        total_asset_value += valuation
        total_units_on_hand += on_hand

        items.append({
            "product_id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "category_name": cat_name or "Umum",
            "unit": prod.unit,
            "on_hand": on_hand,
            "reserved": balance.reserved,
            "available": on_hand - balance.reserved,
            "unit_cogs": unit_cogs,
            "total_valuation": valuation,
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_sku_count": len(items),
        "total_units_on_hand": total_units_on_hand,
        "total_asset_value": total_asset_value,
        "items": items,
    }


async def get_sales_summary_report(
    db: AsyncSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, Any]:
    """Generates Sales & Gross Margin report combining revenue and delivered COGS."""
    # Fetch delivered lines with snapshot COGS
    deliv_stmt = (
        select(DeliveryLine)
        .join(Delivery, DeliveryLine.delivery_id == Delivery.id)
        .options(selectinload(DeliveryLine.product))
    )
    if start_date:
        deliv_stmt = deliv_stmt.where(Delivery.shipped_at >= start_date)
    if end_date:
        deliv_stmt = deliv_stmt.where(Delivery.shipped_at <= end_date)

    deliv_lines = (await db.execute(deliv_stmt)).scalars().all()

    # Fetch issued/paid invoices for revenue
    inv_stmt = select(Invoice).where(
        Invoice.status.in_([InvoiceStatus.TERBIT.value,
                           InvoiceStatus.SEBAGIAN_DIBAYAR.value, InvoiceStatus.LUNAS.value])
    )
    if start_date:
        inv_stmt = inv_stmt.where(Invoice.issued_at >= start_date)
    if end_date:
        inv_stmt = inv_stmt.where(Invoice.issued_at <= end_date)

    invoices = (await db.execute(inv_stmt)).scalars().all()

    gross_revenue = sum(inv.subtotal for inv in invoices)
    total_tax = sum(inv.tax for inv in invoices)
    total_invoiced = sum(inv.total for inv in invoices)

    total_cogs = sum(dl.qty * dl.cogs_at_delivery for dl in deliv_lines)
    gross_profit = gross_revenue - total_cogs
    margin_bp = (gross_profit *
                 10000) // gross_revenue if gross_revenue > 0 else 0

    return {
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
        "gross_revenue": gross_revenue,
        "total_tax": total_tax,
        "total_invoiced": total_invoiced,
        "total_cogs": total_cogs,
        "gross_profit": gross_profit,
        "margin_percentage": f"{margin_bp / 100:.2f}%",
        "invoices_count": len(invoices),
        "delivered_lines_count": len(deliv_lines),
    }


async def get_ar_aging_report(db: AsyncSession) -> dict[str, Any]:
    """Generates Accounts Receivable (Piutang) Aging report grouped by due date brackets."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.customer), selectinload(Invoice.payments))
        .where(Invoice.status.in_([InvoiceStatus.TERBIT.value, InvoiceStatus.SEBAGIAN_DIBAYAR.value]))
        .order_by(Invoice.due_at.asc())
    )
    invoices = (await db.execute(stmt)).scalars().all()

    customer_buckets: dict[int, dict[str, Any]] = {}
    total_ar = 0
    bucket_totals = {
        "current": 0,
        "days_1_30": 0,
        "days_31_60": 0,
        "days_61_90": 0,
        "days_over_90": 0,
    }

    for inv in invoices:
        paid = sum(p.amount for p in inv.payments if p.status ==
                   PaymentStatus.BERHASIL.value)
        unpaid = inv.total - paid
        if unpaid <= 0:
            continue

        cust_id = inv.customer_id
        cust_name = inv.customer.name if inv.customer else "Pelanggan Umum"
        if cust_id not in customer_buckets:
            customer_buckets[cust_id] = {
                "customer_id": cust_id,
                "customer_name": cust_name,
                "current": 0,
                "days_1_30": 0,
                "days_31_60": 0,
                "days_61_90": 0,
                "days_over_90": 0,
                "total_unpaid": 0,
            }

        due_at = inv.due_at
        if due_at and due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)

        days_overdue = (now - due_at).days if due_at and now > due_at else 0

        bucket = "current"
        if days_overdue <= 0:
            bucket = "current"
        elif 1 <= days_overdue <= 30:
            bucket = "days_1_30"
        elif 31 <= days_overdue <= 60:
            bucket = "days_31_60"
        elif 61 <= days_overdue <= 90:
            bucket = "days_61_90"
        else:
            bucket = "days_over_90"

        customer_buckets[cust_id][bucket] += unpaid
        customer_buckets[cust_id]["total_unpaid"] += unpaid
        bucket_totals[bucket] += unpaid
        total_ar += unpaid

    return {
        "generated_at": now.isoformat(),
        "total_ar": total_ar,
        "summary": bucket_totals,
        "customers": list(customer_buckets.values()),
    }


async def get_stock_card_report(
    db: AsyncSession,
    product_id: int,
    limit: int = 100,
) -> dict[str, Any]:
    """Generates chronological Stock Card ledger for a specific product."""
    prod = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if not prod:
        return {"error": "Produk tidak ditemukan"}

    stmt = (
        select(StockMove)
        .where(StockMove.product_id == product_id)
        .order_by(StockMove.id.asc())
        .limit(limit)
    )
    moves = (await db.execute(stmt)).scalars().all()

    running_balance = 0
    records = []

    for m in moves:
        qty_in = m.qty if m.qty > 0 else 0
        qty_out = abs(m.qty) if m.qty < 0 else 0
        running_balance += m.qty

        records.append({
            "id": m.id,
            "created_at": m.created_at.isoformat(),
            "kind": m.kind,
            "ref_type": m.ref_type,
            "ref_id": m.ref_id,
            "qty_in": qty_in,
            "qty_out": qty_out,
            "unit_cost": m.unit_cost,
            "running_balance": running_balance,
        })

    return {
        "product_id": prod.id,
        "sku": prod.sku,
        "name": prod.name,
        "unit": prod.unit,
        "current_cogs": prod.cogs_amount,
        "records": records,
    }


async def check_and_notify_low_stock(
    db: AsyncSession,
    send_telegram: bool = True,
) -> list[dict[str, Any]]:
    """Identifies products below safety threshold and dispatches alerts."""
    stmt = (
        select(Product, StockBalance)
        .join(StockBalance, Product.id == StockBalance.product_id)
        .where(Product.is_active == True, StockBalance.on_hand <= Product.min_stock)
        .order_by(StockBalance.on_hand.asc())
    )
    items = (await db.execute(stmt)).all()

    alerts = []
    notifier = get_telegram_notifier() if send_telegram else None

    for prod, bal in items:
        alert_info = {
            "product_id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "on_hand": bal.on_hand,
            "min_stock": prod.min_stock,
        }
        alerts.append(alert_info)
        if notifier:
            await notifier.notify_low_stock(
                product_name=prod.name,
                sku=prod.sku,
                on_hand=bal.on_hand,
                min_stock=prod.min_stock,
            )

    return alerts


def generate_csv(headers: list[str], rows: list[list[Any]]) -> str:
    """Serializes dataset to RFC-4180 CSV with UTF-8 BOM for spreadsheet compatibility."""
    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()
