import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.domain.enums import (
    DocType,
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
    PurchaseOrderStatus,
    SalesOrderStatus,
    StockMoveKind,
    UserRole,
)
from app.models.audit import AuditLog
from app.models.company import Company
from app.models.doc_sequence import DocSequence
from app.models.invoicing import (
    Invoice,
    InvoiceLine,
    Payment,
    PaymentLink,
    WebhookEvent,
)
from app.models.master import Category, Customer, Product, Supplier
from app.models.purchasing import (
    GoodsReceipt,
    GoodsReceiptLine,
    PurchaseOrder,
    PurchaseOrderLine,
)
from app.models.refresh_token import RefreshToken
from app.models.sales import (
    Delivery,
    DeliveryLine,
    SalesOrder,
    SalesOrderLine,
)
from app.models.stock import StockBalance, StockMove
from app.models.user import User

logger = logging.getLogger(__name__)


async def seed_all_data(db: AsyncSession) -> dict[str, int]:
    """Populates the database with deterministic master and transaction records."""
    now = datetime.now(timezone.utc)

    # 1. Company Profile
    company = Company(
        id=1,
        name="PT Lumbung Pangan Nusantara",
        address="Kawasan Pergudangan Marunda Center Blok A3 No. 8, Jakarta Utara",
        phone="021-88997766",
        email="kontak@lumbungpangan.co.id",
        tax_id_npwp="01.234.567.8-012.000",
        tax_rate_bp=1100,  # PPN 11%
    )
    db.add(company)
    await db.flush()

    # 2. Users (Official Enterprise Accounts)
    pw_hash = hash_password("Lumbung2026!")
    users = [
        User(
            id=1,
            email="dewi.sartika@lumbungpangan.co.id",
            name="Dewi Sartika",
            role=UserRole.ADMIN.value,
            password_hash=pw_hash,
            is_active=True,
        ),
        User(
            id=2,
            email="budi.santoso@lumbungpangan.co.id",
            name="Budi Santoso",
            role=UserRole.SALES.value,
            password_hash=pw_hash,
            is_active=True,
        ),
        User(
            id=3,
            email="siti.rahayu@lumbungpangan.co.id",
            name="Siti Rahayu",
            role=UserRole.WAREHOUSE.value,
            password_hash=pw_hash,
            is_active=True,
        ),
        User(
            id=4,
            email="rudi.hermawan@lumbungpangan.co.id",
            name="Rudi Hermawan",
            role=UserRole.FINANCE.value,
            password_hash=pw_hash,
            is_active=True,
        ),
    ]
    db.add_all(users)
    await db.flush()

    # 3. Categories
    categories = [
        Category(id=1, name="Beras", code="BERAS"),
        Category(id=2, name="Minyak Goreng", code="MINYAK"),
        Category(id=3, name="Gula Pasir", code="GULA"),
        Category(id=4, name="Tepung Terigu", code="TEPUNG"),
    ]
    db.add_all(categories)
    await db.flush()

    # 4. Suppliers
    suppliers = [
        Supplier(
            id=1,
            name="Penggilingan Padi Subang Makmur",
            contact_person="H. Sobri",
            phone="08123456701",
            email="sobri@subangpadi.local",
            address="Jl. Raya Pagaden No. 45, Subang",
            is_active=True,
        ),
        Supplier(
            id=2,
            name="PT Sumber Sawit Sejahtera",
            contact_person="Bambang Wijaya",
            phone="08123456702",
            email="sales@sumbersawit.local",
            address="Kawasan Industri Cikarang Blok C-12",
            is_active=True,
        ),
        Supplier(
            id=3,
            name="Pabrik Gula Rafinasi Nusantara",
            contact_person="Irwan Siregar",
            phone="08123456703",
            email="irwan@gularafinasi.local",
            address="Jl. Pelabuhan Tanjung Priok No. 8",
            is_active=True,
        ),
    ]
    db.add_all(suppliers)
    await db.flush()

    # 5. Customers
    customers = [
        Customer(
            id=1,
            name="Toko Sembako Berkah Jaya",
            contact_person="Ko Ahong",
            phone="08139876501",
            email="berkahjaya@gmail.local",
            address="Pasar Induk Kramat Jati Los B No. 20",
            terms_days=14,
            credit_limit=50000000,
            is_active=True,
        ),
        Customer(
            id=2,
            name="CV Pangan Makmur Abadi",
            contact_person="Ibu Linda",
            phone="08139876502",
            email="makmurabadi@cvemail.local",
            address="Jl. Boulevard Raya Blok QJ No. 5, Kelapa Gading",
            terms_days=30,
            credit_limit=100000000,
            is_active=True,
        ),
        Customer(
            id=3,
            name="Restoran Sari Rasa Minang",
            contact_person="Datuk Maringgai",
            phone="08139876503",
            email="sarirasa@kuliner.local",
            address="Jl. Pemuda No. 77, Rawamangun",
            terms_days=0,  # Tunai / COD
            credit_limit=15000000,
            is_active=True,
        ),
    ]
    db.add_all(customers)
    await db.flush()

    # 6. Products
    products = [
        Product(
            id=1,
            category_id=1,
            sku="BRS-PND-05K",
            name="Beras Pandan Wangi Premium 5kg",
            unit="sak",
            cogs_amount=68000,
            sell_price=76000,
            min_stock=50,
            is_active=True,
        ),
        Product(
            id=2,
            category_id=1,
            sku="BRS-RMS-05K",
            name="Beras Setra Ramos 5kg",
            unit="sak",
            cogs_amount=62000,
            sell_price=69500,
            min_stock=40,
            is_active=True,
        ),
        Product(
            id=3,
            category_id=2,
            sku="MYK-SNI-02L",
            name="Minyak Goreng Sania Pouch 2L",
            unit="pouch",
            cogs_amount=30500,
            sell_price=34500,
            min_stock=100,
            is_active=True,
        ),
        Product(
            id=4,
            category_id=2,
            sku="MYK-TRP-02L",
            name="Minyak Goreng Tropical Botol 2L",
            unit="botol",
            cogs_amount=32000,
            sell_price=36500,
            min_stock=60,
            is_active=True,
        ),
        Product(
            id=5,
            category_id=3,
            sku="GLA-GLK-01K",
            name="Gulaku Gula Tebu Premium 1kg",
            unit="pack",
            cogs_amount=15200,
            sell_price=17500,
            min_stock=80,
            is_active=True,
        ),
        Product(
            id=6,
            category_id=4,
            sku="TPG-SGT-01K",
            name="Tepung Terigu Segitiga Biru 1kg",
            unit="pack",
            cogs_amount=11000,
            sell_price=13000,
            min_stock=50,
            is_active=True,
        ),
    ]
    db.add_all(products)
    await db.flush()

    # 7. Stock Balances & Initial Movements
    initial_stocks = [
        (1, 200, 68000),
        (2, 150, 62000),
        (3, 350, 30500),
        (4, 180, 32000),
        (5, 250, 15200),
        (6, 120, 11000),
    ]

    for p_id, qty, cost in initial_stocks:
        bal = StockBalance(product_id=p_id, on_hand=qty, reserved=0)
        db.add(bal)
        move = StockMove(
            product_id=p_id,
            qty=qty,
            unit_cost=cost,
            kind=StockMoveKind.RECEIPT.value,
            ref_type="INIT",
            ref_id=1,
            notes="Saldo awal inisialisasi sistem",
            created_by=1,
        )
        db.add(move)

    # 8. Purchase Order & Goods Receipt (Completed)
    po1 = PurchaseOrder(
        id=1,
        number="PO-2026-000001",
        supplier_id=1,
        status=PurchaseOrderStatus.SELESAI.value,
        total=13600000,
        order_date=now - timedelta(days=10),
        notes="Pengadaan stok beras awal bulan",
        created_by=1,
    )
    db.add(po1)
    await db.flush()

    po_line1 = PurchaseOrderLine(
        id=1,
        po_id=po1.id,
        product_id=1,
        qty=200,
        unit_price=68000,
        subtotal=13600000,
    )
    db.add(po_line1)

    gr1 = GoodsReceipt(
        id=1,
        number="GR-2026-000001",
        po_id=po1.id,
        received_at=now - timedelta(days=9),
        notes="Diterima lengkap oleh Gudang Siti",
        received_by=3,
    )
    db.add(gr1)
    await db.flush()

    gr_line1 = GoodsReceiptLine(
        id=1,
        gr_id=gr1.id,
        po_line_id=po_line1.id,
        product_id=1,
        qty=200,
        unit_cost=68000,
    )
    db.add(gr_line1)

    # 9. Sales Order 1 (Delivered & Invoiced LUNAS)
    so1 = SalesOrder(
        id=1,
        number="SO-2026-000001",
        customer_id=1,
        status=SalesOrderStatus.SELESAI.value,
        subtotal=2265000,
        tax=249150,
        total=2514150,
        order_date=now - timedelta(days=5),
        created_by=2,
    )
    db.add(so1)
    await db.flush()

    so_line1 = SalesOrderLine(
        id=1,
        so_id=so1.id,
        product_id=1,
        qty=20,
        unit_price=76000,
        discount_bp=0,
        subtotal=1520000,
    )
    so_line2 = SalesOrderLine(
        id=2,
        so_id=so1.id,
        product_id=3,
        qty=20,
        unit_price=34500,
        discount_bp=0,
        subtotal=690000,
    )
    db.add_all([so_line1, so_line2])
    await db.flush()

    deliv1 = Delivery(
        id=1,
        number="DO-2026-000001",
        so_id=so1.id,
        customer_id=1,
        shipped_at=now - timedelta(days=4),
        created_by=3,
    )
    db.add(deliv1)
    await db.flush()

    deliv_line1 = DeliveryLine(
        id=1,
        delivery_id=deliv1.id,
        so_line_id=so_line1.id,
        product_id=1,
        qty=20,
        cogs_at_delivery=68000,
    )
    deliv_line2 = DeliveryLine(
        id=2,
        delivery_id=deliv1.id,
        so_line_id=so_line2.id,
        product_id=3,
        qty=20,
        cogs_at_delivery=30500,
    )
    db.add_all([deliv_line1, deliv_line2])
    await db.flush()

    inv1 = Invoice(
        id=1,
        number="INV-2026-000001",
        customer_id=1,
        status=InvoiceStatus.LUNAS.value,
        subtotal=2210000,
        tax=243100,
        total=2453100,
        issued_at=now - timedelta(days=4),
        due_at=now + timedelta(days=10),
        notes="Faktur lunas via transfer bank",
        created_by=4,
    )
    db.add(inv1)
    await db.flush()

    inv_line1 = InvoiceLine(
        id=1,
        invoice_id=inv1.id,
        delivery_line_id=deliv_line1.id,
        product_id=1,
        qty=20,
        unit_price=76000,
        discount_bp=0,
        subtotal=1520000,
    )
    inv_line2 = InvoiceLine(
        id=2,
        invoice_id=inv1.id,
        delivery_line_id=deliv_line2.id,
        product_id=3,
        qty=20,
        unit_price=34500,
        discount_bp=0,
        subtotal=690000,
    )
    db.add_all([inv_line1, inv_line2])

    pay1 = Payment(
        id=1,
        invoice_id=inv1.id,
        amount=2453100,
        method=PaymentMethod.TRANSFER.value,
        status=PaymentStatus.BERHASIL.value,
        reference="TRF-BCA-88991122",
        paid_at=now - timedelta(days=3),
        created_by=4,
    )
    db.add(pay1)

    # 10. DocSequences seed
    sequences = [
        DocSequence(doc_type=DocType.PO.value, year=2026, current_number=1),
        DocSequence(doc_type=DocType.GR.value, year=2026, current_number=1),
        DocSequence(doc_type=DocType.SO.value, year=2026, current_number=1),
        DocSequence(doc_type=DocType.DO.value, year=2026, current_number=1),
        DocSequence(doc_type=DocType.INV.value, year=2026, current_number=1),
        DocSequence(doc_type=DocType.PAY.value, year=2026, current_number=1),
    ]
    db.add_all(sequences)

    # Commit entire deterministic seed transaction
    await db.commit()

    return {
        "users": len(users),
        "products": len(products),
        "customers": len(customers),
        "suppliers": len(suppliers),
        "initial_stock_items": len(initial_stocks),
    }


async def reset_demo_data(db: AsyncSession) -> dict[str, str]:
    """Wipes all transactional and master tables and regenerates pristine deterministic seeds."""
    logger.info("Memulai reset data demo deterministik...")

    # Wipe in inverse topological order (child first, parent last)
    tables_to_clear = [
        WebhookEvent,
        Payment,
        PaymentLink,
        InvoiceLine,
        Invoice,
        DeliveryLine,
        Delivery,
        SalesOrderLine,
        SalesOrder,
        GoodsReceiptLine,
        GoodsReceipt,
        PurchaseOrderLine,
        PurchaseOrder,
        StockMove,
        StockBalance,
        AuditLog,
        DocSequence,
        RefreshToken,
        Product,
        Category,
        Customer,
        Supplier,
        User,
        Company,
    ]

    for model in tables_to_clear:
        await db.execute(delete(model))

    await db.flush()

    # Re-populate fresh seed
    await seed_all_data(db)

    logger.info("Reset data demo berhasil diselesaikan.")
    return {
        "status": "success",
        "message": "Data demo Lumbung ERP berhasil di-reset ke kondisi awal deterministik.",
    }
