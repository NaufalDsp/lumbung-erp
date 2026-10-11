from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SalesOrderLineCreate(BaseModel):
    product_id: int
    qty: int = Field(..., gt=0, description="Kuantitas harus > 0")
    unit_price: int = Field(..., ge=0,
                            description="Harga satuan dalam rupiah integer")
    discount_bp: int = Field(
        0, ge=0, le=10000, description="Diskon dalam basis points (misal 500 = 5%)")


class SalesOrderLineResponse(BaseModel):
    id: int
    so_id: int
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    qty: int
    unit_price: int
    discount_bp: int
    delivered_qty: int
    gross_amount: int
    discount_amount: int
    subtotal: int

    model_config = ConfigDict(from_attributes=True)


class SalesOrderCreate(BaseModel):
    customer_id: int
    notes: str | None = None
    lines: list[SalesOrderLineCreate] = Field(..., min_length=1)


class SalesOrderUpdate(BaseModel):
    notes: str | None = None
    lines: list[SalesOrderLineCreate] | None = None


class SalesOrderResponse(BaseModel):
    id: int
    number: str | None
    customer_id: int
    customer_name: str | None = None
    status: str
    notes: str | None
    ordered_at: datetime | None
    total_gross: int
    total_discount: int
    total_amount: int
    lines: list[SalesOrderLineResponse]

    model_config = ConfigDict(from_attributes=True)


class DeliveryLineCreate(BaseModel):
    so_line_id: int
    qty: int = Field(..., gt=0)


class DeliveryCreate(BaseModel):
    so_id: int
    notes: str | None = None
    lines: list[DeliveryLineCreate] = Field(..., min_length=1)


class DeliveryLineResponse(BaseModel):
    id: int
    delivery_id: int
    so_line_id: int
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    qty: int
    unit_cost_snapshot: int

    model_config = ConfigDict(from_attributes=True)


class DeliveryResponse(BaseModel):
    id: int
    number: str
    so_id: int
    customer_id: int
    customer_name: str | None = None
    notes: str | None
    delivered_at: datetime
    lines: list[DeliveryLineResponse]

    model_config = ConfigDict(from_attributes=True)
