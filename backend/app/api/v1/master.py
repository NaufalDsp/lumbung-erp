import csv
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthenticatedUser, get_current_user, require_permission
from app.api.v1.schemas.master import (
    CategoryCreate,
    CategoryResponse,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    PaginatedResponse,
    ProductCreate,
    ProductImportResult,
    ProductResponse,
    ProductUpdate,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.core.permissions import Permission
from app.models.database import get_db
from app.models.master import Category, Customer, Product, Supplier
from app.models.stock import StockBalance
from app.services.audit import record_audit_log

router = APIRouter(tags=["Master Data"])


# ==========================================
# CATEGORIES
# ==========================================
@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> list[CategoryResponse]:
    stmt = select(Category).order_by(Category.name.asc())
    result = await db.execute(stmt)
    return [CategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> CategoryResponse:
    existing = await db.execute(select(Category).where(Category.name.ilike(payload.name.strip())))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "KATEGORI_SUDAH_ADA",
                              "message": f"Kategori '{payload.name}' sudah terdaftar"}},
        )

    category = Category(name=payload.name.strip())
    db.add(category)
    await db.flush()

    await record_audit_log(
        db=db,
        entity="category",
        entity_id=category.id,
        action="create",
        actor_id=current_user.id,
        diff={"name": category.name},
    )
    await db.commit()
    return CategoryResponse.model_validate(category)


# ==========================================
# PRODUCTS
# ==========================================
@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    q: str | None = Query(None, description="Pencarian SKU atau nama produk"),
    category_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ProductResponse]:
    stmt = select(Product).options(selectinload(Product.category))
    count_stmt = select(func.count(Product.id))

    if q:
        search_term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.sku.ilike(search_term),
                          Product.name.ilike(search_term)))
        count_stmt = count_stmt.where(or_(Product.sku.ilike(
            search_term), Product.name.ilike(search_term)))

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
        count_stmt = count_stmt.where(Product.category_id == category_id)

    if is_active is not None:
        stmt = stmt.where(Product.is_active == is_active)
        count_stmt = count_stmt.where(Product.is_active == is_active)

    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one() or 0

    offset = (page - 1) * limit
    stmt = stmt.order_by(Product.sku.asc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    products = res.scalars().all()

    items = [
        ProductResponse(
            id=p.id,
            sku=p.sku,
            name=p.name,
            category_id=p.category_id,
            category_name=p.category.name if p.category else None,
            unit=p.unit,
            sell_price=p.sell_price,
            last_buy_price=p.last_buy_price,
            min_stock=p.min_stock,
            is_active=p.is_active,
        )
        for p in products
    ]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> ProductResponse:
    stmt = select(Product).options(selectinload(
        Product.category)).where(Product.id == product_id)
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PRODUK_TIDAK_DITEMUKAN",
                              "message": "Produk tidak ditemukan"}},
        )

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category_id=product.category_id,
        category_name=product.category.name if product.category else None,
        unit=product.unit,
        sell_price=product.sell_price,
        last_buy_price=product.last_buy_price,
        min_stock=product.min_stock,
        is_active=product.is_active,
    )


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> ProductResponse:
    existing_sku = await db.execute(select(Product).where(Product.sku == payload.sku.strip()))
    if existing_sku.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "SKU_DUPLIKAT",
                              "message": f"SKU '{payload.sku}' sudah digunakan"}},
        )

    product = Product(
        sku=payload.sku.strip().upper(),
        name=payload.name.strip(),
        category_id=payload.category_id,
        unit=payload.unit.strip().lower(),
        sell_price=payload.sell_price,
        last_buy_price=payload.last_buy_price,
        min_stock=payload.min_stock,
        is_active=True,
    )
    db.add(product)
    await db.flush()

    # Initialize zero stock balance for warehouse 1
    balance = StockBalance(
        product_id=product.id,
        warehouse_id=1,
        on_hand=0,
        reserved=0,
        avg_cost=payload.last_buy_price,
    )
    db.add(balance)

    await record_audit_log(
        db=db,
        entity="product",
        entity_id=product.id,
        action="create",
        actor_id=current_user.id,
        diff=payload.model_dump(),
    )
    await db.commit()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category_id=product.category_id,
        category_name=None,
        unit=product.unit,
        sell_price=product.sell_price,
        last_buy_price=product.last_buy_price,
        min_stock=product.min_stock,
        is_active=product.is_active,
    )


@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> ProductResponse:
    stmt = select(Product).options(selectinload(
        Product.category)).where(Product.id == product_id)
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PRODUK_TIDAK_DITEMUKAN",
                              "message": "Produk tidak ditemukan"}},
        )

    updates = payload.model_dump(exclude_unset=True)
    diff: dict[str, dict[str, object]] = {}
    for key, value in updates.items():
        old_val = getattr(product, key)
        if old_val != value:
            diff[key] = {"old": old_val, "new": value}
            setattr(product, key, value)

    if diff:
        await record_audit_log(
            db=db,
            entity="product",
            entity_id=product.id,
            action="update",
            actor_id=current_user.id,
            diff=diff,
        )
        await db.commit()

    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category_id=product.category_id,
        category_name=product.category.name if product.category else None,
        unit=product.unit,
        sell_price=product.sell_price,
        last_buy_price=product.last_buy_price,
        min_stock=product.min_stock,
        is_active=product.is_active,
    )


@router.delete("/products/{product_id}")
async def deactivate_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> dict[str, str]:
    """Soft-deactivates product rather than hard-deleting to preserve historical consistency."""
    stmt = select(Product).where(Product.id == product_id)
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PRODUK_TIDAK_DITEMUKAN",
                              "message": "Produk tidak ditemukan"}},
        )

    product.is_active = False
    await record_audit_log(
        db=db,
        entity="product",
        entity_id=product.id,
        action="deactivate",
        actor_id=current_user.id,
        diff={"is_active": False},
    )
    await db.commit()
    return {"message": f"Produk {product.sku} berhasil dinonaktifkan"}


@router.post("/products/import", response_model=ProductImportResult)
async def import_products_csv(
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_PRODUCTS))],
) -> ProductImportResult:
    """CSV Bulk import for products with dry-run error checking per row."""
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "FORMAT_FILE_SALAH",
                              "message": "Berkas CSV harus berformat UTF-8"}},
        )

    reader = csv.DictReader(io.StringIO(decoded))
    imported = 0
    errors: list[dict[str, str | int]] = []

    for row_idx, row in enumerate(reader, start=2):
        sku = (row.get("sku") or "").strip().upper()
        name = (row.get("name") or "").strip()
        unit = (row.get("unit") or "pcs").strip().lower()
        sell_price_str = (row.get("sell_price") or "0").strip()
        buy_price_str = (row.get("last_buy_price") or "0").strip()
        min_stock_str = (row.get("min_stock") or "0").strip()

        if not sku or not name:
            errors.append(
                {"line": row_idx, "error": "SKU dan Nama produk wajib diisi"})
            continue

        try:
            sell_price = int(sell_price_str)
            buy_price = int(buy_price_str)
            min_stock = int(min_stock_str)
        except ValueError:
            errors.append(
                {"line": row_idx, "error": "Harga jual, harga beli, atau stok minimum harus angka"})
            continue

        # Check existing SKU
        check = await db.execute(select(Product).where(Product.sku == sku))
        if check.scalar_one_or_none():
            errors.append({"line": row_idx, "error": f"SKU '{sku}' sudah ada"})
            continue

        prod = Product(
            sku=sku,
            name=name,
            unit=unit,
            sell_price=sell_price,
            last_buy_price=buy_price,
            min_stock=min_stock,
            is_active=True,
        )
        db.add(prod)
        await db.flush()

        db.add(StockBalance(product_id=prod.id, warehouse_id=1,
               on_hand=0, reserved=0, avg_cost=buy_price))
        imported += 1

    if imported > 0:
        await record_audit_log(
            db=db,
            entity="product",
            entity_id=0,
            action="csv_import",
            actor_id=current_user.id,
            diff={"imported_count": imported},
        )
        await db.commit()

    return ProductImportResult(imported_count=imported, errors=errors)


# ==========================================
# CUSTOMERS
# ==========================================
@router.get("/customers", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CustomerResponse]:
    stmt = select(Customer)
    count_stmt = select(func.count(Customer.id))

    if q:
        search = f"%{q.strip()}%"
        stmt = stmt.where(or_(Customer.code.ilike(
            search), Customer.name.ilike(search)))
        count_stmt = count_stmt.where(
            or_(Customer.code.ilike(search), Customer.name.ilike(search)))

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    res = await db.execute(stmt.order_by(Customer.code.asc()).offset(offset).limit(limit))
    items = [CustomerResponse.model_validate(c) for c in res.scalars().all()]
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> CustomerResponse:
    res = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = res.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PELANGGAN_TIDAK_DITEMUKAN",
                              "message": "Pelanggan tidak ditemukan"}},
        )
    return CustomerResponse.model_validate(customer)


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_CUSTOMERS))],
) -> CustomerResponse:
    existing = await db.execute(select(Customer).where(Customer.code == payload.code.strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "KODE_DUPLIKAT",
                              "message": f"Kode pelanggan '{payload.code}' sudah digunakan"}},
        )

    customer = Customer(
        code=payload.code.strip().upper(),
        name=payload.name.strip(),
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        terms_days=payload.terms_days,
        credit_limit=payload.credit_limit,
        is_active=True,
    )
    db.add(customer)
    await db.flush()

    await record_audit_log(
        db=db,
        entity="customer",
        entity_id=customer.id,
        action="create",
        actor_id=current_user.id,
        diff=payload.model_dump(),
    )
    await db.commit()
    return CustomerResponse.model_validate(customer)


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_CUSTOMERS))],
) -> CustomerResponse:
    res = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = res.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PELANGGAN_TIDAK_DITEMUKAN",
                              "message": "Pelanggan tidak ditemukan"}},
        )

    updates = payload.model_dump(exclude_unset=True)
    diff: dict[str, dict[str, object]] = {}
    for key, value in updates.items():
        old = getattr(customer, key)
        if old != value:
            diff[key] = {"old": old, "new": value}
            setattr(customer, key, value)

    if diff:
        await record_audit_log(
            db=db,
            entity="customer",
            entity_id=customer.id,
            action="update",
            actor_id=current_user.id,
            diff=diff,
        )
        await db.commit()

    return CustomerResponse.model_validate(customer)


# ==========================================
# SUPPLIERS
# ==========================================
@router.get("/suppliers", response_model=PaginatedResponse[SupplierResponse])
async def list_suppliers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[SupplierResponse]:
    stmt = select(Supplier)
    count_stmt = select(func.count(Supplier.id))

    if q:
        search = f"%{q.strip()}%"
        stmt = stmt.where(or_(Supplier.code.ilike(
            search), Supplier.name.ilike(search)))
        count_stmt = count_stmt.where(
            or_(Supplier.code.ilike(search), Supplier.name.ilike(search)))

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    res = await db.execute(stmt.order_by(Supplier.code.asc()).offset(offset).limit(limit))
    items = [SupplierResponse.model_validate(s) for s in res.scalars().all()]
    return PaginatedResponse(items=items, total=total, page=page, limit=limit)


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> SupplierResponse:
    res = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = res.scalar_one_or_none()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PEMASOK_TIDAK_DITEMUKAN",
                              "message": "Pemasok tidak ditemukan"}},
        )
    return SupplierResponse.model_validate(supplier)


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_SUPPLIERS))],
) -> SupplierResponse:
    existing = await db.execute(select(Supplier).where(Supplier.code == payload.code.strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "KODE_DUPLIKAT",
                              "message": f"Kode pemasok '{payload.code}' sudah digunakan"}},
        )

    supplier = Supplier(
        code=payload.code.strip().upper(),
        name=payload.name.strip(),
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        is_active=True,
    )
    db.add(supplier)
    await db.flush()

    await record_audit_log(
        db=db,
        entity="supplier",
        entity_id=supplier.id,
        action="create",
        actor_id=current_user.id,
        diff=payload.model_dump(),
    )
    await db.commit()
    return SupplierResponse.model_validate(supplier)


@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(Permission.MANAGE_SUPPLIERS))],
) -> SupplierResponse:
    res = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = res.scalar_one_or_none()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PEMASOK_TIDAK_DITEMUKAN",
                              "message": "Pemasok tidak ditemukan"}},
        )

    updates = payload.model_dump(exclude_unset=True)
    diff: dict[str, dict[str, object]] = {}
    for key, value in updates.items():
        old = getattr(supplier, key)
        if old != value:
            diff[key] = {"old": old, "new": value}
            setattr(supplier, key, value)

    if diff:
        await record_audit_log(
            db=db,
            entity="supplier",
            entity_id=supplier.id,
            action="update",
            actor_id=current_user.id,
            diff=diff,
        )
        await db.commit()

    return SupplierResponse.model_validate(supplier)
