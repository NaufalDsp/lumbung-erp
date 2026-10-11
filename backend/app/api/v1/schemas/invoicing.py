from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import PaymentMethod


class InvoiceLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    delivery_line_id: int
    product_id: int
    qty: int
    unit_price: int
    discount_bp: int
    subtotal: int


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: int
    method: str
    status: str
    reference: str | None
    paid_at: datetime


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str | None
    customer_id: int
    status: str
    subtotal: int
    tax: int
    total: int
    issued_at: datetime | None
    due_at: datetime | None
    notes: str | None
    created_at: datetime
    lines: list[InvoiceLineResponse] = []
    payments: list[PaymentResponse] = []


class CreateInvoiceRequest(BaseModel):
    delivery_ids: list[int] = Field(..., min_length=1,
                                    description="Daftar ID surat jalan yang akan difakturkan")
    notes: str | None = None


class RecordPaymentRequest(BaseModel):
    amount: int = Field(..., gt=0,
                        description="Nominal pembayaran dalam integer Rupiah")
    method: PaymentMethod = Field(
        default=PaymentMethod.TRANSFER, description="Metode pembayaran")
    reference: str | None = Field(
        default=None, description="Nomor bukti transfer atau referensi bank")


class PaymentLinkResponse(BaseModel):
    token: str
    expires_at: datetime
    payment_url: str
    snap_token: str | None = None


class PublicInvoiceLine(BaseModel):
    product_name: str
    qty: int
    unit_price: int
    subtotal: int


class PublicInvoiceResponse(BaseModel):
    number: str
    customer_name: str
    company_name: str
    status: str
    issued_at: datetime | None
    due_at: datetime | None
    subtotal: int
    tax: int
    total: int
    balance_due: int
    lines: list[PublicInvoiceLine]
    snap_token: str | None = None
