from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SALES = "sales"
    WAREHOUSE = "warehouse"
    FINANCE = "finance"


class DocType(str, Enum):
    PO = "PO"   # Purchase Order (Pesanan Pembelian)
    GR = "GR"   # Goods Receipt (Penerimaan Barang)
    SO = "SO"   # Sales Order (Pesanan Penjualan)
    DO = "DO"   # Delivery Order (Pengiriman Barang / Surat Jalan)
    INV = "INV"  # Invoice (Faktur Penjualan)
    PAY = "PAY"  # Payment (Pembayaran)


class SalesOrderStatus(str, Enum):
    DRAF = "draf"
    DIKONFIRMASI = "dikonfirmasi"
    SEBAGIAN_TERKIRIM = "sebagian_terkirim"
    TERKIRIM = "terkirim"
    SELESAI = "selesai"
    BATAL = "batal"


class PurchaseOrderStatus(str, Enum):
    DRAF = "draf"
    DIPESAN = "dipesan"
    SEBAGIAN_DITERIMA = "sebagian_diterima"
    DITERIMA = "diterima"
    BATAL = "batal"


class InvoiceStatus(str, Enum):
    DRAF = "draf"
    TERBIT = "terbit"
    SEBAGIAN_DIBAYAR = "sebagian_dibayar"
    LUNAS = "lunas"
    VOID = "void"


class StockMoveKind(str, Enum):
    PENERIMAAN = "penerimaan"
    PENGIRIMAN = "pengiriman"
    PENYESUAIAN = "penyesuaian"
    KOREKSI = "koreksi"


class StockAdjustmentReason(str, Enum):
    RUSAK = "rusak"
    HILANG = "hilang"
    HASIL_HITUNG_ULANG = "hasil_hitung_ulang"
    LAINNYA = "lainnya"


class PaymentMethod(str, Enum):
    TRANSFER = "transfer"
    MIDTRANS = "midtrans"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    BERHASIL = "berhasil"
    GAGAL = "gagal"
    KEDALUWARSA = "kedaluwarsa"
