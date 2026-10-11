from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int


# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Product Schemas ---
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    category_id: int | None = None
    unit: str = Field("pcs", max_length=20)
    sell_price: int = Field(0, ge=0)
    last_buy_price: int = Field(0, ge=0)
    min_stock: int = Field(0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    category_id: int | None = None
    unit: str | None = Field(None, max_length=20)
    sell_price: int | None = Field(None, ge=0)
    last_buy_price: int | None = Field(None, ge=0)
    min_stock: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    category_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductImportRow(BaseModel):
    sku: str
    name: str
    category_name: str | None = None
    unit: str = "pcs"
    sell_price: int = 0
    last_buy_price: int = 0
    min_stock: int = 0


class ProductImportResult(BaseModel):
    imported_count: int
    errors: list[dict[str, str | int]]


# --- Customer Schemas ---
class CustomerBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    terms_days: int = Field(30, ge=0)
    credit_limit: int = Field(0, ge=0)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    terms_days: int | None = Field(None, ge=0)
    credit_limit: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# --- Supplier Schemas ---
class SupplierBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
