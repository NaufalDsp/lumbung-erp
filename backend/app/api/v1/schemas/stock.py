from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import StockAdjustmentReason


class StockBalanceResponse(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    category_name: str | None = None
    unit: str
    on_hand: int
    reserved: int
    available: int
    avg_cost: int
    total_value: int

    model_config = ConfigDict(from_attributes=True)


class StockMoveResponse(BaseModel):
    id: int
    product_id: int
    product_sku: str | None = None
    product_name: str | None = None
    warehouse_id: int
    qty: int
    kind: str
    doc_type: str
    doc_id: int
    unit_cost: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentCreate(BaseModel):
    product_id: int
    qty_change: int = Field(...,
                            description="Perubahan kuantitas (+ untuk tambah, - untuk kurang)")
    reason: StockAdjustmentReason
    notes: str = Field(..., min_length=3,
                       description="Catatan alasan penyesuaian")


class StockConsistencyReport(BaseModel):
    is_consistent: bool
    discrepancies: list[dict[str, Any]]
