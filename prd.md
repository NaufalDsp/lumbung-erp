# PRD — Lumbung

**Mini ERP alur pesanan sampai faktur**

**Versi:** 1.0
**Penyusun:** Naufal
**Tanggal:** 11 Oktober 2026
**Status:** Draf untuk dieksekusi
**Dokumen pasangan:** `design.md`

> **Tentang nama.** *Lumbung* berarti tempat menyimpan hasil panen: stok yang dijaga, dicatat, dan dikeluarkan dengan teratur. Nama ini sengaja dipilih agar sesuai dengan inti sistem (stok dan transaksi). Silakan ganti kapan saja; nama hanya muncul di judul, wordmark, dan README.
>
> **Asumsi dokumen.** Portofolio ini diarahkan ke posisi **fullstack dengan bobot backend**. Bila targetmu berbeda (data/analyst, misalnya), bagian 6 dan 15 bisa digeser. Perusahaan, produk, pelanggan, dan transaksi di dalam sistem seluruhnya **fiktif**.

---

## 1. Ringkasan

Lumbung adalah sistem manajemen operasional untuk perusahaan dagang kecil: mencatat barang yang dibeli, disimpan, dijual, dikirim, ditagih, dan dibayar. Ia mencakup satu rantai bisnis yang utuh:

```
Pembelian ──► Penerimaan ──► STOK ──► Penjualan ──► Pengiriman ──► Faktur ──► Pembayaran
  (PO)          (GR)        (ledger)     (SO)          (DO)         (INV)       (PAY)
```

Tujuan proyek ini bukan menandingi ERP sungguhan, tetapi **membuktikan kemampuan menangani masalah yang memang sulit di sistem bisnis**: konsistensi stok saat banyak transaksi bersamaan, aturan status dokumen, hak akses berlapis, jejak audit, perhitungan uang tanpa galat pembulatan, dan integrasi dengan layanan pihak ketiga lewat webhook yang aman.

Seluruhnya berjalan di tingkat gratis, dengan tautan demo yang hidup dan akun contoh yang bisa dicoba pengunjung dalam hitungan detik.

---

## 2. Tujuan

### 2.1 Tujuan portofolio
Seorang rekruter atau teknisi yang membuka tautan demo harus bisa:

1. Memahami apa yang dibuat dalam **dua menit** (halaman pembuka menjelaskannya dengan diagram nyata, bukan slogan).
2. Masuk dengan satu klik dan **menjalankan satu alur penuh** (buat pesanan → kirim → terbitkan faktur → bayar) dalam kurang dari lima menit.
3. Menemukan **bukti kualitas rekayasa** tanpa diminta: dokumentasi API otomatis, diagram basis data, tes, pipeline CI, dan keputusan teknis yang dijelaskan.

### 2.2 Tujuan produk
| Tujuan | Ukuran |
|---|---|
| Stok tidak pernah salah | Uji konkurensi: 50 permintaan bersamaan atas stok terbatas tidak pernah menghasilkan stok minus atau pesanan melebihi tersedia |
| Uang tidak pernah selisih | Seluruh nilai uang bertipe bilangan bulat (rupiah); uji properti: jumlah baris = subtotal, subtotal + PPN = total, tanpa selisih |
| Setiap perubahan bisa ditelusuri | Setiap dokumen punya jejak: siapa, kapan, dari status apa ke status apa |
| Aman untuk didemokan | Pengunjung tidak bisa merusak data; data demo dikembalikan otomatis setiap malam |
| Gratis seluruhnya | Tidak ada layanan berbayar di dalam arsitektur v1 |

---

## 3. Pengguna & peran

Lumbung melayani empat peran internal. Pengunjung demo masuk sebagai salah satunya.

| Peran | Tugas harian | Hak utama |
|---|---|---|
| **Admin** | Mengatur sistem | Semua modul, kelola pengguna, pengaturan perusahaan, lihat audit |
| **Penjualan** | Menerima dan mengelola pesanan pelanggan | Pelanggan, pesanan penjualan, lihat stok tersedia, lihat faktur milik pesanannya |
| **Gudang** | Menerima dan mengeluarkan barang | Penerimaan barang, pengiriman, penyesuaian stok, lihat pesanan yang harus disiapkan |
| **Keuangan** | Menagih dan mencatat pembayaran | Faktur, pembayaran, laporan piutang; tidak boleh mengubah stok |

Pelanggan dan pemasok bukan pengguna sistem di v1; mereka hanya data. Pelanggan dapat membuka **tautan pembayaran** untuk satu faktur (tanpa login), lihat 9.2.

Prinsip akses: **hak diberikan berdasarkan tindakan, bukan halaman.** Daftar izin ada di bagian 8.3 dan diuji otomatis.

---

## 4. Metrik keberhasilan

| Ukuran | Target |
|---|---|
| Dari pembukaan tautan sampai masuk sebagai peran demo | ≤ 10 detik (di luar bangun-dari-tidur server) |
| Waktu bangun server dari tidur ditangani tanpa membingungkan | Layar menunggu yang menjelaskan, ≤ 90 detik |
| Waktu respons API p95 (server aktif) | < 400 ms |
| Cakupan tes untuk logika domain (stok, faktur, status) | ≥ 85% |
| Alur utama diuji end-to-end otomatis | 3 alur (penjualan penuh, pembelian penuh, pembayaran lewat webhook) |
| Pipeline CI | Hijau pada `main`; tes, lint, cek tipe, dan cek migrasi |
| Lighthouse (Performance / Accessibility) halaman pembuka | ≥ 90 / ≥ 95 |
| README | Terbaca tuntas dalam < 5 menit; memuat diagram arsitektur, ERD, dan tautan demo |

---

## 5. Prinsip produk

1. **Dokumen adalah pusatnya.** Setiap transaksi adalah dokumen bernomor dengan status, baris, total, dan riwayat. Antarmuka dan kode mengikuti model ini.
2. **Aturan bisnis di satu tempat.** Logika stok, harga, dan status berada di lapisan domain backend, bukan tersebar di komponen React atau di kueri SQL ad hoc.
3. **Buku besar tidak pernah diedit.** Pergerakan stok hanya ditambah, tidak diubah atau dihapus; koreksi dilakukan dengan pergerakan baru yang berlawanan.
4. **Gagal keras di dalam, ramah di luar.** Pelanggaran aturan (stok kurang, status salah) ditolak dengan kode galat yang jelas; pengguna melihat pesan yang bisa ditindaklanjuti.
5. **Kuota gratis adalah anggaran.** Rancangan memperhitungkan server yang tidur, batas email harian, dan ukuran basis data sejak awal.
6. **Buktikan, jangan klaim.** Setiap klaim di README (aman, konsisten, teruji) harus dapat diperiksa lewat tes atau dokumentasi.

---

## 6. Lingkup

### 6.1 Masuk lingkup v1
- **Master data:** produk (SKU, satuan, harga jual, harga beli terakhir, stok minimum), kategori, pelanggan, pemasok.
- **Pembelian:** pesanan pembelian (PO) dan penerimaan barang (GR) parsial maupun penuh.
- **Stok:** buku besar stok, saldo per gudang (satu gudang di v1, skema siap multi-gudang), reservasi stok, penyesuaian stok, peringatan stok minimum.
- **Penjualan:** pesanan penjualan (SO) dengan reservasi stok, pengiriman (DO) parsial maupun penuh.
- **Faktur & pembayaran:** faktur dari pengiriman, PPN, diskon baris, jatuh tempo, pembayaran manual dan lewat Midtrans (sandbox), faktur PDF, pengiriman email.
- **Laporan:** nilai persediaan, kartu stok per produk, umur piutang, penjualan per periode, produk terlaris.
- **Pengguna & hak akses:** empat peran, login email/kata sandi dan Google, akun demo.
- **Jejak audit** untuk seluruh dokumen dan data master.
- **Integrasi pihak ketiga:** Midtrans (sandbox), Telegram Bot, Resend (email), Google OAuth. Detail di bagian 9.
- **Halaman pembuka portofolio** dengan penjelasan proyek, diagram arsitektur, dan akses demo.

### 6.2 Di luar lingkup v1
- Akuntansi lengkap (jurnal umum, buku besar akun, neraca, laba rugi).
- Multi-gudang aktif dan transfer antar gudang (skema disiapkan, antarmuka tidak).
- Multi-mata uang.
- Produksi/BOM, manufaktur, atau modul SDM dan penggajian.
- Retur penjualan dan nota kredit (dicatat di D4 sebagai tahap lanjut).
- E-faktur pajak resmi dan integrasi DJP.
- Aplikasi seluler native.
- Lacak nomor seri atau batch/kedaluwarsa.

---

## 7. Aturan domain

Bagian ini adalah inti proyek. Setiap aturan harus memiliki tes otomatis.

### 7.1 Uang
- Seluruh nilai uang disimpan sebagai **bilangan bulat dalam rupiah** (`BIGINT`). Tidak ada `float`/`decimal` pecahan untuk rupiah.
- **Diskon baris** dalam persen bulat atau nominal; dihitung per baris dan dibulatkan ke rupiah terdekat (setengah naik).
- **PPN** default 11%, dapat diatur di pengaturan. Dihitung **per dokumen** dari jumlah setelah diskon, dibulatkan ke rupiah terdekat.
- Total dokumen = jumlah baris setelah diskon + PPN. Nilai ini dihitung di backend; frontend hanya menampilkan.
- Format tampilan: `Rp 1.250.000` (pemisah ribuan titik, tanpa desimal).

### 7.2 Penomoran dokumen
- Format `{JENIS}-{TAHUN}-{URUT 6 digit}`, mis. `SO-2026-000042`, `INV-2026-000017`.
- Urutan per jenis per tahun, dari tabel `doc_sequences` yang dikunci saat dipakai, sehingga **tanpa nomor ganda dan tanpa lubang akibat konkurensi**.
- Nomor diberikan saat dokumen **dikonfirmasi**, bukan saat draf dibuat; draf memakai penanda sementara.

### 7.3 Status dokumen

**Pesanan penjualan (SO)**
```
draf ──► dikonfirmasi ──► sebagian_terkirim ──► terkirim ──► selesai
  │            │
  └──► batal ◄─┘  (hanya selama belum ada pengiriman)
```
- Konfirmasi: memeriksa dan **mereservasi** stok; gagal bila stok tersedia kurang.
- Batal: melepas reservasi.
- `selesai`: seluruh pengiriman sudah difakturkan dan lunas.

**Pesanan pembelian (PO):** `draf → dipesan → sebagian_diterima → diterima`, atau `batal` sebelum ada penerimaan.

**Faktur (INV):** `draf → terbit → sebagian_dibayar → lunas`; `jatuh_tempo` bukan status tersimpan melainkan **turunan** (terbit/sebagian dibayar dan lewat tanggal jatuh tempo); `void` hanya bila belum ada pembayaran.

Setiap perpindahan status melewati satu fungsi mesin status yang menolak perpindahan tidak sah dan menulis jejak audit.

### 7.3.1 Dokumen tidak bisa diubah setelah terbit
Setelah dikonfirmasi (SO/PO) atau diterbitkan (INV), baris dan harga **dikunci**. Koreksi dilakukan dengan membatalkan (bila diizinkan) dan membuat dokumen baru.

### 7.4 Stok
- **Buku besar** `stock_moves`: hanya tambah. Setiap baris: produk, gudang, jumlah (positif masuk, negatif keluar), jenis (`penerimaan`, `pengiriman`, `penyesuaian`, `koreksi`), dokumen sumber, biaya satuan, waktu, pelaku.
- **Saldo** `stock_balances` (produk × gudang): `on_hand`, `reserved`. `tersedia = on_hand − reserved`. Saldo diperbarui dalam transaksi yang sama dengan penulisan buku besar.
- **Invarian:** `on_hand` selalu sama dengan jumlah `stock_moves` produk itu; `reserved ≥ 0`; `on_hand ≥ 0`. Diperiksa oleh tes dan oleh pemeriksa konsistensi terjadwal.
- **Reservasi:** dibuat saat SO dikonfirmasi, dikurangi bertahap saat pengiriman, dilepas saat batal.
- **Konkurensi:** pembaruan saldo memakai `SELECT … FOR UPDATE` pada baris saldo, dalam urutan produk yang konsisten (menghindari kebuntuan). Pelanggaran invarian ditolak dengan galat `STOK_TIDAK_CUKUP`.
- **Penyesuaian stok** wajib berisi alasan dari daftar (rusak, hilang, hasil hitung ulang, lainnya) dan komentar.

### 7.5 Penilaian persediaan
- Metode **rata-rata bergerak** (moving average) per produk.
- Saat penerimaan: `biaya_rata2_baru = (nilai_lama + nilai_masuk) / (qty_lama + qty_masuk)`, dibulatkan ke rupiah.
- Saat pengiriman: HPP = `qty × biaya_rata2` saat itu; biaya rata-rata tidak berubah oleh pengeluaran.
- Nilai persediaan = Σ `on_hand × biaya_rata2`.

### 7.6 Faktur dari pengiriman
- Faktur dibuat dari satu atau beberapa pengiriman milik pesanan yang sama; baris faktur membawa harga dari SO (bukan harga master saat ini).
- Satu pengiriman tidak boleh difakturkan dua kali (kunci unik pada relasi pengiriman–faktur).
- Jatuh tempo = tanggal terbit + termin pelanggan (hari).

### 7.7 Pembayaran
- Satu faktur dapat dibayar bertahap. Jumlah pembayaran tidak boleh melebihi sisa tagihan.
- Pembayaran dari Midtrans bersifat **idempoten**: notifikasi yang sama diproses sekali walau diterima berulang.
- Status faktur dihitung ulang dari jumlah pembayaran yang berstatus berhasil.

---

## 8. Arsitektur & stack

### 8.1 Gambaran umum

```
 Pengunjung / pengguna
        │
        ▼
 ┌─────────────────────────┐        ┌───────────────────────────┐
 │ React (Vite, TS)        │  HTTPS │ FastAPI (Python 3.12)      │
 │ Cloudflare Pages        │ ─────► │ Render (web service gratis)│
 └─────────────────────────┘        └──────┬──────────────┬──────┘
                                           │              │
                                           ▼              ▼
                                   PostgreSQL (Neon)   Integrasi
                                                      ├─ Midtrans (sandbox) ◄─ webhook
                                                      ├─ Telegram Bot API
                                                      ├─ Resend (email)
                                                      └─ Google OAuth

 GitHub Actions (cron): keepalive, cek stok minimum, tandai jatuh tempo,
                        pemeriksa konsistensi stok, reset data demo (malam)
```

### 8.2 Pilihan teknologi

| Lapisan | Pilihan | Alasan |
|---|---|---|
| Frontend | React 19, Vite, TypeScript | Sesuai keahlianmu; build cepat |
| Data di frontend | TanStack Query, TanStack Table | Cache dan status muat; tabel data besar dengan urut/filter |
| Formulir | React Hook Form + Zod | Validasi bertipe; skema bisa dipakai ulang |
| Klien API | Dihasilkan dari OpenAPI (`openapi-typescript`) | Tipe frontend selalu sinkron dengan backend |
| Backend | FastAPI, Pydantic v2 | Dokumentasi OpenAPI otomatis; validasi bawaan |
| ORM & migrasi | SQLAlchemy 2.0, Alembic | Standar industri; migrasi bisa ditinjau di CI |
| Basis data | PostgreSQL | Transaksi, kunci baris, batasan, indeks parsial |
| Autentikasi | JWT akses pendek + refresh token di cookie httpOnly; Argon2id untuk kata sandi | Praktik umum yang aman |
| PDF | `fpdf2` atau ReportLab (Python murni) | Hindari pustaka sistem berat di server gratis |
| Tes | pytest, Hypothesis (properti), Playwright (e2e) | Domain diuji dengan properti, alur diuji end-to-end |
| CI/CD | GitHub Actions | Gratis untuk repositori publik |
| Hosting frontend | Cloudflare Pages | Statis, CDN, SSL |
| Hosting backend | Render (web service gratis) | Menjalankan proses Python tanpa kartu |
| Basis data hosting | Neon (Postgres gratis) | Lihat 8.4 |
| Pemantauan | Log terstruktur JSON + endpoint `/health`; Sentry opsional | Cukup untuk portofolio |

### 8.3 Matriks izin (ringkas)

| Tindakan | Admin | Penjualan | Gudang | Keuangan |
|---|:-:|:-:|:-:|:-:|
| Kelola pengguna & pengaturan | ✓ | | | |
| Ubah master produk | ✓ | | ✓ | |
| Ubah master pelanggan | ✓ | ✓ | | ✓ |
| Buat & konfirmasi SO | ✓ | ✓ | | |
| Buat PO / konfirmasi PO | ✓ | | ✓ | |
| Terima barang (GR) | ✓ | | ✓ | |
| Buat pengiriman (DO) | ✓ | | ✓ | |
| Penyesuaian stok | ✓ | | ✓ | |
| Terbitkan faktur | ✓ | | | ✓ |
| Catat pembayaran | ✓ | | | ✓ |
| Lihat nilai persediaan & HPP | ✓ | | | ✓ |
| Lihat jejak audit | ✓ | | | |

Matriks ini disimpan sebagai data (`permissions`) dan dipakai oleh dependensi FastAPI. Satu tes memeriksa setiap sel matriks terhadap setiap endpoint.

### 8.4 Batas tingkat gratis yang menentukan desain

Dicek lewat pencarian pada 11 Oktober 2026. Angka seperti ini berubah; **cek ulang di dashboard masing-masing sebelum mulai**.

| Layanan | Fakta yang ditemukan | Dampak ke desain |
|---|---|---|
| **Render** (web service gratis) | Server tidur setelah sekitar 15 menit tanpa permintaan masuk, dan sekitar satu menit untuk bangun. Jam instans gratis dibagi dalam satu workspace (sekitar 750 jam/bulan). **Basis data Postgres gratis milik Render kedaluwarsa setelah 30 hari** | Jangan pakai Postgres Render. Frontend harus punya layar "server sedang bangun". Ping berkala hanya membantu, bukan jaminan resmi |
| **Neon** (Postgres gratis) | 0,5 GB penyimpanan dan 100 CU-jam komputasi per proyek per bulan, tanpa kartu dan tanpa kedaluwarsa. Komputasi suspend otomatis setelah sekitar 5 menit idle; kueri pertama setelah idle bisa terlambat beberapa detik | Data demo harus kecil (< 200 MB). Kueri pertama diberi batas waktu yang longgar |
| **Resend** (email) | 3.000 email/bulan dan maksimum 100/hari pada paket gratis; satu domain terverifikasi (sumber berbeda soal jumlahnya) | Pengiriman email demo dibatasi dan dihitung; tanpa domain terverifikasi, pengiriman umumnya hanya ke alamat pemilik akun — cek saat mendaftar |
| **Cloudflare Pages** | Hosting statis gratis dengan CDN dan SSL | Aman untuk frontend |
| **Midtrans Sandbox** | Lingkungan uji gratis dengan kunci terpisah dari produksi | Cukup untuk demo pembayaran; tidak ada uang sungguhan |
| **Telegram Bot API** | Gratis | Aman untuk notifikasi |

### 8.5 Strategi menghadapi server yang tidur
- **Keepalive terjadwal** lewat GitHub Actions setiap 10 menit pada jam kerja (cron GitHub tidak presisi). Dianggap sebagai peredam, bukan jaminan.
- **Layar menunggu yang jujur:** bila permintaan pertama lebih dari 3 detik, frontend menampilkan penjelasan singkat ("Server demo gratis sedang bangun, biasanya sekitar satu menit") dengan indikator yang bergerak.
- **Halaman pembuka statis:** penjelasan proyek, diagram, dan tangkapan layar tidak bergantung pada backend, sehingga rekruter tetap mendapat nilai walau server sedang tidur.
- **Pemanasan saat halaman pembuka dibuka:** halaman pembuka mengirim satu permintaan `/health` di latar belakang, supaya server mulai bangun selagi pengunjung membaca.

---

## 9. Integrasi pihak ketiga

### 9.1 Ringkasan
| Layanan | Fungsi di Lumbung | Mode |
|---|---|---|
| Midtrans | Tautan pembayaran faktur dan notifikasi status | Sandbox |
| Telegram Bot | Notifikasi operasional ke Admin/Keuangan | Bot sungguhan, data fiktif |
| Resend | Mengirim faktur PDF lewat email | Dibatasi untuk demo |
| Google OAuth | Masuk dengan Google | OAuth sungguhan |

### 9.2 Midtrans (pembayaran)
1. Keuangan menerbitkan faktur → tombol **"Buat tautan pembayaran"** memanggil backend, yang meminta transaksi Snap ke Midtrans dengan `order_id` unik per upaya pembayaran.
2. Pelanggan membuka tautan `/bayar/{token}` (tanpa login; token acak, kedaluwarsa, hanya untuk satu faktur) dan membayar lewat Snap sandbox.
3. Midtrans memanggil **`POST /api/webhooks/midtrans`**:
   - **Verifikasi tanda tangan:** hitung SHA-512 dari `order_id + status_code + gross_amount + server_key` dan bandingkan dengan `signature_key` memakai perbandingan waktu-konstan; tolak bila tidak cocok.
   - **Idempotensi:** simpan setiap notifikasi mentah di `webhook_events` dengan kunci unik (`order_id + transaction_status + transaction_time`); notifikasi yang sama tidak diproses ulang.
   - **Verifikasi silang:** sebelum mengubah faktur, panggil API status Midtrans untuk memastikan statusnya sama dengan isi notifikasi.
   - **Efek:** bila `settlement`/`capture` berhasil → catat pembayaran, hitung ulang status faktur, kirim notifikasi Telegram.
4. Notifikasi yang datang tak berurutan (mis. `pending` setelah `settlement`) tidak boleh menurunkan status.
- **Uji:** kumpulan tes memutar ulang notifikasi duplikat, tanda tangan palsu, jumlah tidak cocok, dan urutan terbalik.

### 9.3 Telegram Bot (notifikasi)
- Peristiwa yang dikirim: pesanan baru dikonfirmasi, stok di bawah minimum, pembayaran diterima, faktur jatuh tempo.
- Pengguna menautkan akun lewat perintah `/start <kode>` pada bot; kode berlaku 10 menit dan sekali pakai.
- Pesan ringkas, berisi nomor dokumen dan tautan ke halaman dokumen.
- Pengiriman dilakukan di tugas latar (tidak memblokir permintaan); kegagalan dicatat dan diulang paling banyak tiga kali.

### 9.4 Resend (email faktur)
- Tombol **"Kirim faktur"** membuat PDF dan mengirimnya sebagai lampiran.
- Mode demo: pengunjung memasukkan alamat emailnya sendiri; dibatasi 3 email per sesi dan jumlah total harian dijaga di bawah 100. Bila kuota harian habis, tombol menampilkan pesan yang menjelaskan, bukan galat.
- Setiap pengiriman tercatat di `email_log` (status, waktu, dokumen).

### 9.5 Google OAuth
- Alur kode otorisasi dengan PKCE. Akun Google baru **tidak otomatis mendapat peran**; ia masuk sebagai "menunggu persetujuan" kecuali dalam mode demo, di mana ia diberi peran terbatas (hanya-baca).
- Tidak ada data Google selain email dan nama yang disimpan.

### 9.6 Prinsip untuk semua integrasi
- Kunci dan rahasia hanya berupa variabel lingkungan; tidak pernah di repositori.
- Setiap panggilan keluar punya batas waktu, percobaan ulang terbatas, dan penanganan galat yang tidak menjatuhkan alur utama.
- Setiap integrasi dibungkus **antarmuka tipis** (`PaymentGateway`, `Notifier`, `Mailer`) sehingga dapat diganti atau ditiru (mock) di tes.
- Mode ejek (`FAKE`) tersedia untuk pengembangan lokal dan CI tanpa kunci.

---

## 10. Model data

### 10.1 Tabel inti

| Tabel | Kolom penting | Catatan |
|---|---|---|
| `users` | id, email, name, password_hash, role, is_active, google_sub, created_at | Peran: admin/sales/warehouse/finance |
| `companies` (pengaturan) | name, address, tax_rate_bp, invoice_footer, default_terms_days | Satu baris; `tax_rate_bp` dalam basis poin (1100 = 11%) |
| `categories` | id, name | |
| `products` | id, sku, name, category_id, unit, sell_price, last_buy_price, min_stock, is_active | `sku` unik |
| `customers` | id, code, name, email, phone, address, terms_days, credit_limit | |
| `suppliers` | id, code, name, email, phone, address | |
| `warehouses` | id, code, name | Satu baris di v1 |
| `purchase_orders`, `purchase_order_lines` | PO: id, number, supplier_id, status, ordered_at / baris: product_id, qty, unit_cost | |
| `goods_receipts`, `goods_receipt_lines` | GR: id, number, po_id, received_at / baris: product_id, qty, unit_cost | Menghasilkan `stock_moves` |
| `sales_orders`, `sales_order_lines` | SO: id, number, customer_id, status, ordered_at / baris: product_id, qty, unit_price, discount_bp | Harga dikunci setelah konfirmasi |
| `deliveries`, `delivery_lines` | DO: id, number, so_id, delivered_at / baris: product_id, qty, unit_cost_snapshot | Menghasilkan `stock_moves` dan HPP |
| `invoices`, `invoice_lines` | INV: id, number, customer_id, status, issued_at, due_at, subtotal, tax, total / baris menaut ke delivery_line | Unik pada delivery_line |
| `payments` | id, invoice_id, amount, method (`transfer`/`midtrans`), status, reference, paid_at, created_by | |
| `payment_links` | id, invoice_id, token_hash, midtrans_order_id, expires_at | Token disimpan sebagai hash |
| `stock_moves` | id, product_id, warehouse_id, qty, kind, doc_type, doc_id, unit_cost, created_at, created_by | **Hanya tambah** |
| `stock_balances` | product_id, warehouse_id, on_hand, reserved, avg_cost, version | Kunci utama gabungan |
| `doc_sequences` | doc_type, year, last_value | Dikunci saat dipakai |
| `audit_log` | id, actor_id, entity, entity_id, action, from_status, to_status, diff (jsonb), created_at | Hanya tambah |
| `webhook_events` | id, provider, event_key (unik), payload (jsonb), processed_at, result | Idempotensi |
| `email_log` | id, doc_type, doc_id, to_hash, status, created_at | Alamat disimpan sebagai hash |
| `refresh_tokens` | id, user_id, token_hash, expires_at, revoked_at | |

### 10.2 Batasan yang dipaksakan oleh basis data

```sql
-- Stok tidak boleh minus dan reservasi tidak boleh melebihi yang ada
ALTER TABLE stock_balances
  ADD CONSTRAINT chk_on_hand_nonneg   CHECK (on_hand >= 0),
  ADD CONSTRAINT chk_reserved_nonneg  CHECK (reserved >= 0),
  ADD CONSTRAINT chk_reserved_le_hand CHECK (reserved <= on_hand);

-- Satu pengiriman tidak boleh difakturkan dua kali
CREATE UNIQUE INDEX uq_invoice_line_delivery_line
  ON invoice_lines (delivery_line_id);

-- Notifikasi webhook yang sama tidak diproses ulang
CREATE UNIQUE INDEX uq_webhook_event_key
  ON webhook_events (provider, event_key);

-- Nomor dokumen unik per jenis
CREATE UNIQUE INDEX uq_so_number ON sales_orders (number) WHERE number IS NOT NULL;

-- Buku besar stok tidak boleh diubah atau dihapus
CREATE RULE no_update_stock_moves AS ON UPDATE TO stock_moves DO INSTEAD NOTHING;
CREATE RULE no_delete_stock_moves AS ON DELETE TO stock_moves DO INSTEAD NOTHING;
```

> Basis data adalah garis pertahanan terakhir. Aturan yang sama juga dicek di lapisan domain agar pesan galatnya ramah; batasan SQL memastikan bahwa **bug di kode tetap tidak bisa merusak data**.

### 10.3 Indeks awal
- `products (sku)`, `products (name)` pencarian trigram.
- `sales_orders (customer_id, ordered_at DESC)`, `invoices (status, due_at)`.
- `stock_moves (product_id, created_at DESC)` untuk kartu stok.
- `audit_log (entity, entity_id, created_at DESC)`.

---

## 11. Spesifikasi fitur

### F1 — Autentikasi & akun demo — *M1*
- Login email + kata sandi; Google OAuth (9.5).
- Token akses 15 menit; refresh token httpOnly 14 hari, dapat dicabut.
- **Akun demo:** tombol "Masuk sebagai Admin / Penjualan / Gudang / Keuangan" pada halaman pembuka. Setiap sesi demo menerima pengguna demo bersama dengan token berumur pendek; tidak ada kata sandi yang ditampilkan.
- Pembatasan laju pada login dan pembuatan sesi demo.
- **Diterima bila:** setiap endpoint menolak peran yang tidak berhak (diuji terhadap matriks 8.3).

### F2 — Master data — *M2*
- Daftar dengan pencarian, filter, urut, dan penomoran halaman sisi server; buat/ubah dengan validasi; nonaktifkan, bukan hapus, bila sudah dipakai di dokumen.
- Impor produk dari CSV dengan pratinjau galat per baris sebelum disimpan.
- **Diterima bila:** SKU ganda ditolak; produk yang dipakai tidak bisa dihapus.

### F3 — Pembelian & penerimaan — *M3*
- Buat PO dari pemasok dengan baris produk; konfirmasi menjadi `dipesan`.
- Terima barang sebagian atau penuh; setiap penerimaan menambah `stock_moves`, memperbarui saldo, dan menghitung ulang biaya rata-rata (7.5).
- **Diterima bila:** menerima lebih dari yang dipesan ditolak (atau memerlukan konfirmasi eksplisit dengan alasan); uji properti memastikan nilai persediaan konsisten dengan buku besar.

### F4 — Stok — *M3*
- Saldo per produk (on hand, reservasi, tersedia, nilai).
- Kartu stok per produk: setiap pergerakan, dokumen sumber, saldo berjalan.
- Penyesuaian stok dengan alasan wajib.
- Peringatan stok minimum di dashboard dan Telegram.
- Pemeriksa konsistensi: membandingkan `on_hand` dengan jumlah buku besar; menandai selisih.
- **Diterima bila:** uji konkurensi 50 permintaan paralel tidak pernah melanggar invarian (7.4).

### F5 — Penjualan & pengiriman — *M4*
- Buat SO dengan baris produk, diskon, dan pelanggan; draf dapat diubah bebas.
- Konfirmasi: memberi nomor, memeriksa dan mereservasi stok, mengunci harga.
- Pengiriman sebagian atau penuh; setiap pengiriman mengeluarkan stok, mengurangi reservasi, dan menyimpan HPP saat itu.
- Batal sebelum pengiriman melepas reservasi.
- **Diterima bila:** konfirmasi gagal dengan `STOK_TIDAK_CUKUP` dan pesan yang menyebut produk serta jumlah tersedia; mesin status menolak perpindahan tidak sah.

### F6 — Faktur — *M5*
- Buat faktur dari pengiriman yang belum difakturkan (pilih satu atau beberapa).
- Hitung subtotal, PPN, total sesuai 7.1; terbitkan dengan nomor dan jatuh tempo.
- Cetak/unduh PDF; kirim lewat email (9.4).
- Void bila belum ada pembayaran.
- **Diterima bila:** uji properti membuktikan jumlah baris, subtotal, PPN, dan total selalu konsisten untuk masukan acak.

### F7 — Pembayaran — *M5*
- Catat pembayaran manual (transfer) dengan tanggal dan referensi.
- Buat tautan pembayaran Midtrans; halaman publik `/bayar/{token}`.
- Webhook idempoten dan terverifikasi (9.2).
- Status faktur dihitung ulang otomatis.
- **Diterima bila:** semua skenario uji webhook di 9.2 lulus.

### F8 — Laporan — *M6*
- Nilai persediaan per produk dan total.
- Kartu stok.
- Umur piutang (belum jatuh tempo, 1–30, 31–60, > 60 hari).
- Penjualan per periode dan produk terlaris.
- Ekspor CSV untuk setiap tabel laporan.
- **Diterima bila:** angka laporan cocok dengan perhitungan manual pada data seed (tes pembanding).

### F9 — Jejak audit — *M2 s.d. M6 (tumbuh bersama modul)*
- Setiap perubahan status dan setiap perubahan data master tercatat: siapa, kapan, apa yang berubah.
- Halaman audit (Admin) dengan filter entitas, pelaku, dan waktu.
- Tampilan "riwayat" pada setiap dokumen.

### F10 — Notifikasi — *M6*
- Telegram (9.3) untuk empat peristiwa.
- Pengaturan per pengguna: peristiwa mana yang diterima.

### F11 — Halaman pembuka portofolio — *M1 (kerangka), M7 (lengkap)*
- Penjelasan dua menit: masalah, solusi, alur dokumen, dan keputusan teknis penting.
- Diagram arsitektur dan ERD yang nyata (dibuat dari skema sebenarnya, bukan hiasan).
- Tombol demo per peran, dengan satu kalimat tentang apa yang bisa dicoba tiap peran.
- Tautan ke repositori, dokumentasi API, dan README.
- Bagian "Catatan jujur": batas tier gratis, hal yang sengaja tidak dibuat, dan yang akan dikerjakan berikutnya.

### F12 — Reset data demo — *M7*
- Tugas malam (GitHub Actions memanggil endpoint internal dengan rahasia): menghapus data transaksi dan memuat ulang data seed yang sama.
- Pengguna demo hanya dapat mengubah data dalam batas kuota (mis. maksimal 30 dokumen baru per hari) untuk melindungi basis data 0,5 GB.
- Peringatan terlihat bila ukuran basis data mendekati 70% kuota.

---

## 12. API

Seluruh endpoint di bawah `/api/v1`, dokumentasi di `/docs` (Swagger) dan `/redoc`. Penomoran halaman berbasis kursor; kesalahan memakai format seragam:

```json
{ "error": { "code": "STOK_TIDAK_CUKUP", "message": "Stok tersedia 4, diminta 10", "details": { "product_id": 17, "available": 4, "requested": 10 } } }
```

| Kelompok | Contoh endpoint |
|---|---|
| Auth | `POST /auth/login`, `/auth/refresh`, `/auth/google/callback`, `POST /auth/demo/{role}` |
| Master | `GET/POST/PATCH /products`, `/customers`, `/suppliers`, `POST /products/import` |
| Pembelian | `POST /purchase-orders`, `POST /purchase-orders/{id}/confirm`, `POST /goods-receipts` |
| Stok | `GET /stock/balances`, `GET /stock/moves?product_id=`, `POST /stock/adjustments` |
| Penjualan | `POST /sales-orders`, `POST /sales-orders/{id}/confirm`, `/cancel`, `POST /deliveries` |
| Faktur | `POST /invoices`, `POST /invoices/{id}/issue`, `/void`, `GET /invoices/{id}/pdf`, `POST /invoices/{id}/email` |
| Pembayaran | `POST /payments`, `POST /invoices/{id}/payment-link`, `GET /public/pay/{token}` |
| Laporan | `GET /reports/inventory-valuation`, `/ar-aging`, `/sales-summary` |
| Audit | `GET /audit?entity=&entity_id=` |
| Webhook | `POST /webhooks/midtrans` (tanpa auth sesi; diverifikasi tanda tangan) |
| Internal | `POST /internal/jobs/{nama}` (header rahasia; untuk cron) |
| Kesehatan | `GET /health` |

Setiap `POST` yang mengubah keadaan menerima header opsional **`Idempotency-Key`**; kunci yang sama dalam 24 jam mengembalikan hasil yang sama tanpa efek ganda.

---

## 13. Kebutuhan non-fungsional

### 13.1 Keamanan
- Kata sandi Argon2id; token akses pendek; refresh token dapat dicabut dan dirotasi.
- Otorisasi diperiksa di server untuk setiap tindakan; tidak ada pemeriksaan hanya di frontend.
- CORS hanya untuk domain frontend; CSP ketat pada frontend.
- Webhook diverifikasi tanda tangannya; endpoint internal dilindungi rahasia dan IP bila memungkinkan.
- Token tautan pembayaran disimpan sebagai hash, acak 128-bit, kedaluwarsa, dan hanya berlaku untuk satu faktur.
- Pembatasan laju: login, sesi demo, tautan pembayaran, email.
- Tidak ada data pribadi nyata; alamat email pengunjung disimpan sebagai hash di log.
- Pemindaian dependensi otomatis (Dependabot) dan `pip-audit`/`npm audit` di CI.

### 13.2 Performa
- Semua daftar memakai penomoran halaman sisi server dan indeks yang sesuai.
- Hindari kueri N+1 (dicek lewat tes yang menghitung jumlah kueri pada endpoint utama).
- Respons ringkas: tidak mengirim kolom yang tidak ditampilkan.

### 13.3 Keandalan & data
- Setiap perubahan stok dan dokumen terjadi dalam **satu transaksi basis data**; kegagalan membatalkan seluruhnya.
- Pemeriksa konsistensi stok berjalan terjadwal dan melaporkan selisih.
- Migrasi Alembic diperiksa di CI (dapat naik dan turun pada basis data kosong).
- Cadangan: ekspor `pg_dump` mingguan via GitHub Actions ke artefak, disimpan 4 minggu.

### 13.4 Aksesibilitas & kegunaan
- Seluruh alur utama dapat dioperasikan dengan papan ketik; kontras minimum WCAG AA.
- Status tidak hanya dibedakan lewat warna (selalu ada teks).
- Detail ada di `design.md`.

### 13.5 Observabilitas
- Log terstruktur JSON dengan `request_id`, pengguna, dan durasi.
- `/health` menampilkan status aplikasi dan basis data.
- Halaman status internal (Admin) menampilkan: versi, ukuran basis data, waktu keepalive terakhir, hasil pemeriksa konsistensi.

---

## 14. Strategi pengujian

| Jenis | Cakupan | Alat |
|---|---|---|
| Unit domain | Hitungan uang, pembulatan, penomoran, biaya rata-rata, mesin status | pytest |
| Properti | Total faktur konsisten; nilai persediaan = Σ buku besar; urutan acak penerimaan/pengiriman tidak menghasilkan stok minus | Hypothesis |
| Konkurensi | 50 permintaan paralel pada stok terbatas | pytest + `asyncio`/thread pada Postgres nyata |
| Integrasi API | Setiap endpoint dengan basis data nyata di CI | pytest + layanan Postgres di GitHub Actions |
| Izin | Setiap sel matriks 8.3 terhadap setiap endpoint | Tes berparameter |
| Webhook | Duplikat, tanda tangan palsu, jumlah beda, urutan terbalik | pytest |
| End-to-end | Penjualan penuh, pembelian penuh, pembayaran via webhook | Playwright |
| Kontrak | Skema OpenAPI tidak berubah tanpa disengaja | Diff skema di CI |

Target: ≥ 85% cakupan untuk lapisan domain; CI gagal bila turun.

---

## 15. Risiko

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Server demo tidur | Pengunjung mengira situs rusak | Halaman pembuka statis, pemanasan latar belakang, layar menunggu yang menjelaskan, keepalive |
| Basis data 0,5 GB penuh | Demo berhenti | Data seed kecil, kuota dokumen per hari, reset malam, peringatan 70% |
| Pengunjung merusak atau menyalahgunakan demo | Data kotor, kuota habis | Peran terbatas, pembatasan laju, reset malam, tidak ada unggahan berkas |
| Kuota email 100/hari habis | Fitur email gagal | Batas per sesi, pesan jelas, mode "pratinjau PDF" sebagai alternatif |
| Batas gratis berubah | Arsitektur perlu disesuaikan | Antarmuka tipis untuk setiap layanan, dokumentasi keputusan, pengecekan ulang berkala |
| Lingkup melebar menjadi "ERP sungguhan" | Tak pernah selesai | Daftar "di luar lingkup" dikunci; ide baru masuk daftar tunggu |
| Bug konkurensi di stok | Kredibilitas proyek | Batasan basis data + tes konkurensi + pemeriksa konsistensi |
| Webhook palsu | Faktur ditandai lunas tanpa bayar | Tanda tangan, verifikasi silang ke API Midtrans, idempotensi |

---

## 16. Keputusan terbuka

| # | Pertanyaan | Rekomendasi | Dibutuhkan sebelum |
|---|---|---|---|
| D1 | Posisi yang dituju (fullstack, backend, data)? | Fullstack dengan bobot backend (asumsi dokumen ini) | M0 |
| D2 | Nama proyek tetap *Lumbung*? | Ya; ganti bila ada kecocokan lebih baik | M0 |
| D3 | Backend di Render gratis, atau mencoba penyedia lain? | Render + keepalive; cek ulang syarat saat mendaftar | M0 |
| D4 | Retur dan nota kredit masuk v1? | Tidak; masuk tahap lanjut | M4 |
| D5 | Tunjukkan satu gudang saja atau antarmuka multi-gudang? | Satu gudang; skema siap multi-gudang | M3 |
| D6 | Domain kustom untuk email Resend? | Opsional; tanpa domain, email demo terbatas | M5 |
| D7 | Repositori publik penuh? | Ya, dengan data fiktif dan tanpa rahasia | M0 |
| D8 | Bahasa antarmuka: Indonesia saja atau dwibahasa? | Indonesia untuk antarmuka; kode, komit, dan README dalam bahasa Inggris agar mudah dibaca rekruter internasional | M1 |

---

## 17. Struktur repositori

```
lumbung/
├─ backend/
│  ├─ app/
│  │  ├─ api/            # router FastAPI per kelompok
│  │  ├─ domain/         # aturan bisnis murni (uang, stok, status, penomoran)
│  │  ├─ services/       # orkestrasi transaksi (use case)
│  │  ├─ models/         # SQLAlchemy
│  │  ├─ integrations/   # payment_gateway, notifier, mailer (+ versi FAKE)
│  │  ├─ core/           # konfigurasi, keamanan, logging
│  │  └─ main.py
│  ├─ migrations/        # Alembic
│  ├─ tests/             # unit, properti, konkurensi, integrasi, izin, webhook
│  └─ pyproject.toml
├─ frontend/
│  ├─ src/
│  │  ├─ pages/          # pembuka, masuk, dokumen, laporan
│  │  ├─ features/       # sales, purchasing, stock, invoicing, ...
│  │  ├─ components/     # tabel data, bidang uang, stepper status, ...
│  │  ├─ api/            # klien hasil generate dari OpenAPI
│  │  └─ styles/         # token dari design.md
│  └─ e2e/               # Playwright
├─ seed/                 # skrip data fiktif deterministik
├─ docs/
│  ├─ architecture.md    # diagram + keputusan
│  ├─ erd.md
│  └─ decisions/         # catatan keputusan teknis (ADR) singkat
├─ .github/workflows/    # ci, keepalive, jobs, backup, demo-reset
├─ design.md
├─ prd.md
└─ README.md
```

**Aturan arsitektur:** `domain/` tidak boleh mengimpor FastAPI, SQLAlchemy, atau integrasi; hanya Python murni. Ini yang membuat aturan bisnis mudah diuji dan mudah dibaca.

Variabel lingkungan (nilai di Render/Cloudflare/GitHub Secrets): `DATABASE_URL`, `JWT_SECRET`, `FRONTEND_ORIGIN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `MIDTRANS_SERVER_KEY`, `MIDTRANS_CLIENT_KEY`, `MIDTRANS_IS_PRODUCTION=false`, `TELEGRAM_BOT_TOKEN`, `RESEND_API_KEY`, `INTERNAL_JOB_SECRET`, `DEMO_MODE`.

---

## 18. Roadmap & definisi selesai

**M0 — Fondasi.** Repositori, struktur, CI dasar, Neon dan Render terhubung, `/health` hidup, migrasi pertama, halaman pembuka kosong tayang.
*Selesai bila:* pipeline hijau dan tautan publik menampilkan status backend.

**M1 — Autentikasi & kerangka.** Pengguna, peran, login, Google OAuth, akun demo, kerangka UI (navigasi, tata letak, layar menunggu), matriks izin beserta tesnya.
*Selesai bila:* keempat peran bisa masuk dan melihat menu sesuai hak mereka.

**M2 — Master data & audit.** Produk, kategori, pelanggan, pemasok, impor CSV, jejak audit dasar.
*Selesai bila:* data master dikelola penuh dan setiap perubahan tercatat.

**M3 — Pembelian & stok.** PO, penerimaan barang, buku besar stok, saldo, kartu stok, penyesuaian, biaya rata-rata, pemeriksa konsistensi.
*Selesai bila:* tes properti dan konkurensi stok lulus.

**M4 — Penjualan & pengiriman.** SO, reservasi, mesin status, pengiriman, HPP.
*Selesai bila:* alur penjualan sampai pengiriman berjalan end-to-end dan diuji otomatis.

**M5 — Faktur & pembayaran.** Faktur, PDF, email (Resend), pembayaran manual, Midtrans sandbox dan webhook, halaman bayar publik.
*Selesai bila:* semua skenario webhook lulus dan pembayaran sandbox menandai faktur lunas.

**M6 — Laporan & notifikasi.** Laporan persediaan, piutang, penjualan; ekspor CSV; Telegram.
*Selesai bila:* angka laporan cocok dengan perhitungan pembanding pada data seed.

**M7 — Pengemasan portofolio.** Halaman pembuka lengkap, diagram, README, ADR, data seed realistis, reset malam, kuota demo, keepalive, pengujian di ponsel nyata, cadangan.
*Selesai bila:* orang asing dapat membuka tautan dan menyelesaikan satu alur penuh tanpa bantuan.

> **Perkiraan waktu.** Untuk satu orang yang bekerja paruh waktu, M0–M7 realistisnya beberapa bulan, bukan beberapa minggu. Bila waktu terbatas, **berhenti di M5** sudah menghasilkan portofolio yang kuat; M6 dan M7 menambah polesan, tetapi M7 (pengemasan) jangan dilewatkan.

---

## 19. Dari nol sampai tayang — daftar periksa

**Akun & repositori**
- [ ] Buat akun GitHub, Cloudflare, Render, Neon, Midtrans (sandbox), Telegram (BotFather), Resend, Google Cloud (OAuth)
- [ ] Buat repositori dengan struktur bagian 17; aktifkan Dependabot

**Backend**
- [ ] Neon: buat proyek dan basis data; simpan `DATABASE_URL`
- [ ] Jalankan migrasi; muat data seed
- [ ] Render: hubungkan repositori, set perintah mulai dan variabel lingkungan
- [ ] Uji `/health` dan `/docs` di URL publik

**Frontend**
- [ ] Cloudflare Pages: hubungkan repositori, set `VITE_API_URL`
- [ ] Atur CORS di backend ke domain Pages

**Integrasi**
- [ ] Midtrans sandbox: salin kunci server dan klien; setel URL notifikasi ke `/api/v1/webhooks/midtrans`
- [ ] Telegram: buat bot, simpan token, uji `/start <kode>`
- [ ] Resend: buat kunci API; verifikasi domain bila ada
- [ ] Google OAuth: buat klien OAuth; set URI pengalihan

**Otomasi**
- [ ] Workflow keepalive, tugas terjadwal, reset demo malam, cadangan mingguan
- [ ] Rahasia `INTERNAL_JOB_SECRET` terpasang di Render dan GitHub

**Sebelum dibagikan**
- [ ] Coba setiap peran dari perangkat bersih (jendela penyamaran)
- [ ] Uji dari ponsel dengan koneksi lambat, termasuk layar "server bangun"
- [ ] Jalankan 3 alur e2e terhadap lingkungan publik
- [ ] Tinjau README: tautan demo, diagram, ERD, cara menjalankan lokal, keputusan teknis, catatan jujur
- [ ] Pastikan tidak ada rahasia di riwayat Git

---

## 20. Kerangka README (bagian dari definisi selesai)

1. Satu kalimat tentang apa itu Lumbung, dengan tautan demo dan tangkapan layar utama.
2. Alur dokumen (diagram) dan peran.
3. **Keputusan teknis yang layak dibaca:** buku besar stok yang hanya bertambah, uang sebagai bilangan bulat, penguncian baris untuk konkurensi, idempotensi webhook, batasan di basis data.
4. Arsitektur dan alasan memilih layanan gratis, dengan batasannya.
5. Cara menjalankan secara lokal (satu perintah untuk menyalakan basis data dan data seed).
6. Cara menjalankan tes, termasuk tes konkurensi.
7. Daftar integrasi dan cara mengujinya.
8. Catatan jujur: yang sengaja tidak dibuat dan yang direncanakan berikutnya.

---

*PRD Lumbung v1.0 — dokumen hidup. Tutup keputusan di bagian 16 satu per satu dan catat tanggalnya.*
