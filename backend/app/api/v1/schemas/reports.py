from datetime import datetime
from pydantic import BaseModel


class StockValuationItem(BaseModel):
    product_id: int
    sku: str
    name: str
    category_name: str
    unit: str
    on_hand: int
    reserved: int
    available: int
    unit_cogs: int
    total_valuation: int


class StockValuationResponse(BaseModel):
    generated_at: str
    total_sku_count: int
    total_units_on_hand: int
    total_asset_value: int
    items: list[StockValuationItem]


class SalesSummaryResponse(BaseModel):
    period: dict[str, str | None]
    gross_revenue: int
    total_tax: int
    total_invoiced: int
    total_cogs: int
    gross_profit: int
    margin_percentage: str
    invoices_count: int
    delivered_lines_count: int


class CustomerAgingBucket(BaseModel):
    customer_id: int
    customer_name: str
    current: int
    days_1_30: int
    days_31_60: int
    days_61_90: int
    days_over_90: int
    total_unpaid: int


class ARAgingResponse(BaseModel):
    generated_at: str
    total_ar: int
    summary: dict[str, int]
    customers: list[CustomerAgingBucket]


class StockCardRecord(BaseModel):
    id: int
    created_at: str
    kind: str
    ref_type: str | None
    ref_id: int | None
    qty_in: int
    qty_out: int
    unit_cost: int | None
    running_balance: int


class StockCardResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    unit: str
    current_cogs: int
    records: list[StockCardRecord]


class LowStockItem(BaseModel):
    product_id: int
    sku: str
    name: str
    on_hand: int
    min_stock: int
