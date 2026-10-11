# Lumbung — Mini ERP

> Mini ERP alur pesanan sampai faktur untuk perusahaan dagang: Pembelian (PO) →
> Penerimaan (GR) → Stok (Buku Besar) → Penjualan (SO) → Pengiriman (DO) →
> Faktur (INV) → Pembayaran (Midtrans).

Sistem manajemen operasional terintegrasi yang dirancang dengan **Clean
Architecture**, **Domain-Driven Design (DDD) taktis**, dan akurasi finansial
berbasis bilangan bulat rupiah.

---

## Alur Dokumen

```
Pembelian (PO) ──► Penerimaan (GR) ──► STOK (Ledger) ──► Penjualan (SO) ──► Pengiriman (DO) ──► Faktur (INV) ──► Pembayaran (PAY)
```

## Keputusan Teknis Penting

1. **Uang Sebagai Bilangan Bulat (`BIGINT`):** Seluruh nilai uang disimpan dalam
   satuan Rupiah integer murni tanpa titik kambang (_zero rounding drift_).
2. **Buku Besar Stok Append-Only (`stock_moves`):** Mutasi stok tidak pernah
   diedit atau dihapus. Dilindungi oleh database rules/triggers.
3. **Penanganan Konkurensi Stok:** Penguncian baris (`SELECT ... FOR UPDATE`)
   dengan pengurutan produk konsisten untuk mencegah kondisi balapan (_race
   condition_) dan kebuntuan (_deadlock_).
4. **Idempotensi Webhook:** Webhook pembayaran Midtrans diverifikasi menggunakan
   SHA-512 constant-time comparison dan dilindungi tabel `webhook_events`.
5. **Clean Architecture:** Lapisan domain murni Python tanpa ketergantungan pada
   web framework (FastAPI) maupun ORM (SQLAlchemy).

---

## Struktur Repositori

```
lumbung/
├── backend/            # FastAPI + Python 3.12 (Clean Architecture)
├── frontend/           # React 19 + TypeScript + Vite + TanStack
├── docs/               # Dokumentasi arsitektur, implementasi & ADR
├── seed/               # Generator data fiktif deterministik
└── .github/workflows/  # CI/CD, keepalive, dan nightly demo reset
```

---

## Panduan Menjalankan Secara Lokal

### Kebutuhan Sistem

- Python >= 3.12
- Node.js >= 20
- PostgreSQL >= 15

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -e .
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```
