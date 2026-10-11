from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderLineCreate(BaseModel):
    product_id: int
    qty: int = Field(..., gt=0, description="Kuantitas pesanan harus > 0")
    unit_cost: int = Field(..., ge=0,
                           description="Biaya satuan dalam rupiah integer")


class PurchaseOrderLineResponse(BaseModel):
    id: int
    po_id: int
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    qty: int
    unit_cost: int
    received_qty: int
    subtotal: int

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    notes: str | None = None
    lines: list[PurchaseOrderLineCreate] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    notes: str | None = None
    lines: list[PurchaseOrderLineCreate] | None = None


class PurchaseOrderResponse(BaseModel):
    id: int
    number: str | None
    supplier_id: int
    supplier_name: str | None = None
    status: str
    notes: str | None
    ordered_at: datetime | None
    total_amount: int
    lines: list[PurchaseOrderLineResponse]

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptLineCreate(BaseModel):
    po_line_id: int
    qty: int = Field(..., gt=0)


class GoodsReceiptCreate(BaseModel):
    po_id: int
    notes: str | None = None
    lines: list[GoodsReceiptLineCreate] = Field(..., min_length=1)


class GoodsReceiptLineResponse(BaseModel):
    id: int
    gr_id: int
    po_line_id: int
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    qty: int
    unit_cost: int

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptResponse(BaseModel):
    id: int
    number: str
    po_id: int
    supplier_id: int
    supplier_name: str | None = None
    notes: str | None
    received_at: datetime
    lines: list[GoodsReceiptLineResponse]

    model_config = ConfigDict(from_attributes=True)
