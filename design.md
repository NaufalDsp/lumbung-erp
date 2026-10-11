# DESIGN — Lumbung

**Sistem desain untuk mini ERP alur pesanan sampai faktur**

**Versi:** 1.0
**Tanggal:** 11 Oktober 2026
**Dokumen pasangan:** `prd.md`

> **Cara membaca dokumen ini.** Ini spesifikasi yang bisa langsung diterjemahkan ke token CSS dan komponen React, bukan moodboard. Istilah teknis (nomor dokumen, status, peran) mengikuti `prd.md`. Antarmuka Lumbung adalah **alat kerja yang padat**, sedangkan halaman pembuka portofolio adalah **halaman penjelasan yang tenang**. Keduanya berbagi token yang sama tetapi punya karakter berbeda; bagian 2 menjelaskan pembagiannya.

---

## 1. Arah visual

**Satu kalimat:** buku besar yang rapi, bukan dasbor yang ramai.

Lumbung dirancang seperti dokumen dagang yang baik: kolom yang sejajar, angka yang mudah dibandingkan, garis tipis yang menuntun mata, dan status yang terbaca sekilas. Orang yang memakai ERP seharian butuh **kepadatan yang tenang**, bukan kartu besar berikon dan angka raksasa.

### 1.1 Gagasan penuntun
| Gagasan | Artinya dalam antarmuka |
|---|---|
| **Dokumen sebagai pusat** | Setiap transaksi tampil seperti dokumen: kepala (nomor, pihak, tanggal, status), baris, total, riwayat. Bukan kumpulan kartu |
| **Angka adalah warga kelas satu** | Angka rata kanan, huruf monospasi bertabel, pemisah ribuan konsisten; kolom uang tidak pernah bergeser |
| **Garis, bukan kotak** | Struktur dibentuk garis `1px` dan jarak, bukan bayangan dan kartu bersarang |
| **Status terbaca tanpa warna** | Setiap status punya teks dan bentuk penanda; warna hanya penguat |
| **Papan ketik dulu** | Perintah cepat, pintasan, dan navigasi baris dengan panah; tetikus opsional |
| **Warna dijatah** | Antarmuka netral hangat; warna dipakai hanya untuk makna (status, galat, tindakan utama) |

### 1.2 Daftar larangan (kriteria tolak saat review)
Setiap butir berlaku untuk **seluruh** aplikasi dan halaman pembuka.

- Gradien ungu–biru atau gradien mesh sebagai latar, tombol, atau teks.
- Dasbor berisi deretan kartu statistik dengan ikon bulat berwarna dan angka raksasa di tengah.
- Kartu `rounded-2xl` dengan bayangan lembut dan border tipis di mana-mana.
- Glassmorphism, blur latar, atau efek "kaca".
- Emoji atau ikon bergaya kartun sebagai penanda fungsi.
- Ilustrasi 3D/isometrik orang memegang grafik di keadaan kosong.
- Teks sapaan "Selamat datang kembali, 👋" dan salinan generik bergaya SaaS ("Tingkatkan produktivitas bisnis Anda").
- Grafik hias tanpa data nyata di baliknya; grafik hanya ada bila menjawab pertanyaan.
- Badge pil di setiap sel tabel (status diberi penanda yang lebih tenang, lihat 6.6).
- Animasi masuk pada setiap elemen saat halaman dimuat; animasi memantul (bounce).
- Mode gelap berupa pembalikan warna asal-asalan.
- Teks placeholder "Lorem ipsum", "John Doe", "Acme Corp", atau data contoh yang jelas palsu. Data fiktif harus **masuk akal dan konsisten** (lihat 11).

---

## 2. Dua register

| | **Aplikasi** (di balik login) | **Halaman pembuka** (publik) |
|---|---|---|
| Tujuan | Bekerja cepat dan akurat | Menjelaskan proyek dalam dua menit |
| Kepadatan | Tinggi (baris 36px; mode padat 30px) | Lapang (ruang bernapas besar) |
| Tipografi | Sans UI + mono untuk angka | Serif display untuk judul, sans untuk isi |
| Warna | Netral hangat, aksen hemat | Sama, dengan satu bagian gelap untuk jeda |
| Gerak | Nyaris tak ada | Satu pengungkapan halus saat halaman dibuka |
| Isi | Tabel, formulir, dokumen | Diagram nyata, langkah alur, tombol demo |

---

## 3. Warna

Netral hangat sebagai dasar (seperti kertas dokumen), aksen hijau lumut tua sebagai penanda merek dan tindakan utama, serta satu warna hangat untuk perhatian.

### 3.1 Token inti (mode terang)

| Token | Hex | Peran |
|---|---|---|
| `--paper` | `#F7F4EC` | Latar halaman |
| `--surface` | `#FFFFFF` | Permukaan dokumen, tabel, panel |
| `--surface-2` | `#EFEBE0` | Baris sekunder, kepala tabel, bidang nonaktif |
| `--surface-hover` | `#F3EFE4` | Baris saat disorot |
| `--line` | `#DDD7C8` | Garis pemisah |
| `--line-strong` | `#BFB8A5` | Garis penegas, batas bidang |
| `--ink` | `#1D1C17` | Teks utama |
| `--ink-2` | `#4F4C42` | Teks sekunder |
| `--ink-3` | `#7A7667` | Teks tersier (hanya ≥ 14px atau label pendamping) |
| `--grain` | `#2F4A3A` | **Aksen merek**: tombol utama, tautan, fokus |
| `--grain-hover` | `#243A2D` | Aksen saat disorot |
| `--grain-wash` | `#E4ECE3` | Latar lembut untuk baris terpilih |
| `--amber` | `#9A5B13` | Perhatian: stok menipis, jatuh tempo dekat |
| `--amber-wash` | `#F5E7CF` | Latar peringatan |
| `--brick` | `#A63A2B` | Galat, void, melewati jatuh tempo |
| `--brick-wash` | `#F6E1DC` | Latar galat |
| `--moss` | `#3C6B3F` | Berhasil, lunas, terkirim |
| `--moss-wash` | `#E1EEDF` | Latar berhasil |
| `--slate` | `#4A5A6A` | Informasi netral, draf |
| `--slate-wash` | `#E4E9EE` | Latar informasi |

### 3.2 Token mode gelap

| Token | Hex |
|---|---|
| `--paper` | `#16150F` |
| `--surface` | `#1E1D16` |
| `--surface-2` | `#27261D` |
| `--surface-hover` | `#2B2A21` |
| `--line` | `#38362B` |
| `--line-strong` | `#514F40` |
| `--ink` | `#EDE9DC` |
| `--ink-2` | `#B8B4A3` |
| `--ink-3` | `#8A8675` |
| `--grain` | `#8FBF98` |
| `--grain-hover` | `#A9D2B1` |
| `--grain-wash` | `#223228` |
| `--amber` | `#E0A257` |
| `--brick` | `#E3796A` |
| `--moss` | `#83BC86` |
| `--slate` | `#9DB1C4` |

(`*-wash` pada mode gelap memakai warna dasarnya pada opasitas 14% di atas `--surface`.)

### 3.3 Pasangan kontras
| Pasangan | Rasio perkiraan | Status |
|---|---|---|
| `ink` di atas `paper` | ±16 : 1 | AAA |
| `ink-2` di atas `surface` | ±8,6 : 1 | AAA |
| `ink-3` di atas `surface` | ±4,6 : 1 | AA (≥ 14px) |
| `grain` di atas `surface` | ±9 : 1 | AAA |
| putih di atas `grain` (tombol utama) | ±9 : 1 | AAA |
| `brick` di atas `surface` | ±5,6 : 1 | AA |
| `amber` di atas `surface` | ±5,2 : 1 | AA |

> Rasio dihitung perkiraan; **verifikasi dengan alat kontras** sebelum rilis dan simpan hasilnya di `docs/`.

### 3.4 Aturan pemakaian
- `--grain` hanya untuk: tombol utama, tautan, cincin fokus, dan baris terpilih. **Tidak** untuk dekorasi.
- Warna status (`moss`, `amber`, `brick`, `slate`) hanya untuk status dan galat; tidak untuk menghias kepala bagian.
- Satu tombol utama (`--grain`) per layar atau per dialog.
- Latar halaman `--paper`, permukaan dokumen `--surface`; tidak ada tingkat ketiga.

---

## 4. Tipografi

| Peran | Keluarga | Bobot | Catatan |
|---|---|---|---|
| UI, formulir, tabel, tombol | **Public Sans** | 400, 500, 600 | Jernih di ukuran kecil, ramah angka |
| Angka, nomor dokumen, SKU, kode | **IBM Plex Mono** | 400, 500 | Bertabel; dipakai untuk semua nilai uang dan jumlah |
| Judul halaman pembuka | **Newsreader** (opsi optik) | 400, 500 | Hanya di halaman pembuka |

> Tiga keluarga dengan peran tegas: dua di aplikasi, satu tambahan di halaman pembuka. Semua di-*self-host*, di-subset Latin, `font-display: swap`. Bila Newsreader terasa kurang cocok setelah dicoba, alternatif: `Source Serif 4` atau `Fraunces` bobot rendah.

### 4.1 Skala (aplikasi)

| Token | Ukuran | Line-height | Pemakaian |
|---|---|---|---|
| `--t-page` | 22px | 1.25 | Judul halaman ("Pesanan Penjualan") |
| `--t-doc` | 20px | 1.25 | Nomor dokumen di kepala dokumen |
| `--t-section` | 14px, 600, huruf kapital, `letter-spacing: .04em` | 1.3 | Judul bagian dalam dokumen |
| `--t-body` | 14px | 1.45 | Isi, sel tabel |
| `--t-small` | 12.5px | 1.4 | Keterangan, metadata |
| `--t-num` | 14px mono | 1.45 | Angka dalam tabel |
| `--t-total` | 18px mono 500 | 1.2 | Total dokumen |

### 4.2 Skala (halaman pembuka)
| Token | Ukuran | Pemakaian |
|---|---|---|
| `--t-hero` | `clamp(2.5rem, 6vw, 5rem)`, serif 400, line-height 1.02 | Judul utama |
| `--t-h2` | `clamp(1.75rem, 3vw, 2.5rem)`, serif | Judul bagian |
| `--t-lead` | `clamp(1.125rem, 1.5vw, 1.375rem)`, sans | Pengantar |
| `--t-body-lg` | 17px, line-height 1.7, maks 68ch | Isi penjelasan |

### 4.3 Aturan angka dan uang
- Semua uang: `font-variant-numeric: tabular-nums`, mono, **rata kanan**, tanpa desimal: `Rp 1.250.000`.
- Simbol `Rp` berwarna `--ink-3`, angkanya `--ink`; simbol tidak ikut diratakan dalam kolom (ditata dengan lebar tetap).
- Nilai negatif: tanda minus, warna `--brick`, bukan kurung.
- Jumlah barang: bilangan bulat tanpa pemisah di bawah 1.000; satuan dalam `--ink-3` setelah angka ("24 pcs").
- Tanggal: `11 Okt 2026` (tabel), `11 Oktober 2026` (dokumen). Waktu relatif ("3 jam lalu") hanya untuk aktivitas, dengan tanggal penuh pada `title`.
- Tidak pernah memotong nomor dokumen dengan elipsis.

---

## 5. Tata letak & ruang

### 5.1 Kerangka aplikasi

```
┌──────┬──────────────────────────────────────────────────────┐
│      │  Bilah atas: perintah cepat (Ctrl+K) · status server │
│ NAV  ├──────────────────────────────────────────────────────┤
│ 220px│  Judul halaman                       [Tombol utama]  │
│      │  ─────────────────────────────────────────────────── │
│      │                                                      │
│      │  Konten (tabel, dokumen, formulir)                   │
│      │                                                      │
└──────┴──────────────────────────────────────────────────────┘
```

- **Navigasi samping:** 220px, dapat diciutkan menjadi 56px (hanya singkatan dua huruf, bukan ikon dekoratif). Dikelompokkan menurut alur kerja: *Penjualan*, *Pembelian*, *Stok*, *Keuangan*, *Laporan*, *Master*, *Sistem*. Tampilkan hanya bagian yang boleh diakses peran.
- **Bilah atas:** 48px. Kiri: breadcrumb. Tengah: kolom perintah cepat. Kanan: indikator server ("Server aktif" / "Server bangun…"), nama pengguna + peran, sakelar tema.
- **Konten:** lebar penuh dengan batas `1280px` untuk formulir dan dokumen; tabel boleh selebar layar.

### 5.2 Ukuran dan ritme
| Elemen | Nilai |
|---|---|
| Satuan dasar | 4px |
| Skala ruang | 4, 8, 12, 16, 24, 32, 48, 64 |
| Tinggi baris tabel | 36px (nyaman), 30px (padat) |
| Tinggi bidang formulir | 36px |
| Tinggi tombol | 36px (normal), 30px (kecil) |
| Padding halaman | 24px (desktop), 16px (tablet), 12px (ponsel) |

### 5.3 Breakpoint
`480` · `768` · `1024` · `1280`. Aplikasi dirancang **desktop-pertama** (ini alat kerja), dengan perilaku tablet dan ponsel yang sungguh dipikirkan, bukan sekadar menyusut (lihat 9).

### 5.4 Bentuk
- **Radius:** bidang dan tombol `4px`, dialog `6px`, penanda status `2px`. Tidak ada radius di atas 6px, kecuali avatar lingkaran.
- **Bayangan:** hanya satu, untuk elemen yang mengambang (menu, dialog, perintah cepat): `0 8px 24px rgba(29,28,23,.14)`. Tidak ada bayangan pada kartu atau tabel.
- **Garis:** `1px --line`; garis penegas `1px --line-strong`; bidang aktif memakai cincin fokus (lihat 6.2).

---

## 6. Komponen

### 6.1 Tabel data (komponen paling penting)
- Kepala tabel: latar `--surface-2`, teks `--t-small` 600, huruf kapital semua **tidak** dipakai; urut ditandai panah kecil dan `aria-sort`.
- Baris: garis bawah `1px --line`; tanpa selang-seling warna. Sorotan baris dengan `--surface-hover`; baris terpilih `--grain-wash` dengan garis kiri `2px --grain`.
- Kolom uang dan jumlah: rata kanan, mono; kolom teks rata kiri; kolom status rata kiri.
- **Kepala tetap** (sticky) dan kolom pertama (nomor dokumen) tetap saat menggulir ke samping.
- Alat di atas tabel: kolom cari (kiri), filter (chip yang dapat dihapus), pilihan kepadatan, ekspor CSV (kanan).
- Penomoran halaman di bawah: "1–50 dari 1.284", tombol sebelumnya/berikutnya, pilihan jumlah baris. Kursor di server, tetapi antarmuka tetap tampak seperti halaman.
- **Navigasi papan ketik:** panah atas/bawah memindahkan baris aktif, `Enter` membuka dokumen, `Spasi` memilih, `/` memfokuskan pencarian.
- Keadaan kosong, memuat, dan galat dijelaskan di 7.

### 6.2 Tombol dan bidang
| Varian | Rupa | Pemakaian |
|---|---|---|
| **Utama** | Latar `--grain`, teks putih, radius 4px | Satu per layar: tindakan inti ("Konfirmasi pesanan") |
| **Sekunder** | Latar `--surface`, garis `--line-strong`, teks `--ink` | Tindakan lain |
| **Tersier** | Tanpa latar, teks `--grain`, garis bawah saat hover | Tautan dan tindakan ringan |
| **Berbahaya** | Latar `--brick`, teks putih | Batal/void, hanya setelah konfirmasi |

- **Fokus:** cincin `2px --grain` dengan offset 2px pada semua elemen interaktif; terlihat jelas, tidak pernah dimatikan.
- **Bidang teks:** latar `--surface`, garis `--line-strong`, label **di atas** bidang (bukan placeholder sebagai label), pesan galat di bawah dalam `--brick` dengan awalan teks "Galat:" agar tidak hanya bergantung pada warna.
- **Bidang uang:** rata kanan, mono, otomatis memformat saat kehilangan fokus, awalan "Rp" tetap.
- **Bidang jumlah:** tombol naik/turun tidak dipakai; ketik langsung, `↑/↓` mengubah satu unit.
- **Pemilih entitas** (pelanggan, produk): bidang cari dengan hasil bertabel kecil (kode, nama, info pendukung seperti stok tersedia), bisa dijangkau penuh lewat papan ketik.
- Tombol berhenti merespons dan menampilkan indikator kecil saat permintaan berjalan; tidak ada putaran layar penuh.

### 6.3 Kepala dokumen
Setiap dokumen (SO, PO, DO, INV, GR) memakai kerangka yang sama sehingga pengguna selalu tahu di mana mencari apa.

```
┌────────────────────────────────────────────────────────────────┐
│ SO-2026-000042                         ● Dikonfirmasi          │
│ Pesanan Penjualan                                              │
│ ────────────────────────────────────────────────────────────── │
│ Pelanggan  CV Tirta Mandiri         Tanggal    11 Okt 2026     │
│ Termin     30 hari                  Dibuat oleh  Rina (Penjualan)│
├────────────────────────────────────────────────────────────────┤
│ ① Draf  ──  ② Dikonfirmasi  ──  ③ Terkirim  ──  ④ Selesai      │  stepper status
└────────────────────────────────────────────────────────────────┘
```

- Nomor dokumen dalam mono `--t-doc`, selalu bisa disalin (klik menyalin, dengan umpan balik singkat).
- **Stepper status:** garis horizontal dengan titik; tahap berjalan diisi, tahap lewat diberi tanda, tahap berikut dipudarkan. Bila `batal`, stepper diganti satu baris "Dibatalkan oleh … pada …".
- Tombol tindakan di kanan atas hanya menampilkan tindakan yang **sah pada status saat ini dan boleh bagi peran itu**; sisanya disembunyikan, bukan dinonaktifkan tanpa penjelasan. Bila sengaja dinonaktifkan, tooltip menyebut alasannya.

### 6.4 Tabel baris dokumen dan total
- Baris dokumen dapat disunting langsung selama berstatus draf: `Tab` pindah antar sel, `Enter` pada sel terakhir menambah baris baru, `Ctrl+Backspace` menghapus baris.
- Setelah dikonfirmasi, baris menjadi hanya-baca dengan ikon kunci kecil dan keterangan "Harga dikunci".
- Blok total di kanan bawah, lebar tetap, rata kanan, dipisah garis:

```
                          Jumlah          Rp 12.450.000
                          Diskon          Rp   -450.000
                          Setelah diskon  Rp 12.000.000
                          PPN 11%         Rp  1.320.000
                          ─────────────────────────────
                          TOTAL           Rp 13.320.000
```
- Baris total memakai mono 18px; total akhir berat 500 dengan garis ganda di atasnya.
- Tidak ada angka yang dihitung di sisi klien untuk disimpan; klien menampilkan **hasil dari server** (hitungan sementara di draf diberi penanda "perkiraan").

### 6.5 Garis waktu riwayat
- Di panel samping dokumen: daftar vertikal peristiwa dari jejak audit ("Dikonfirmasi oleh Rina · 11 Okt 14:02", "Harga baris 3 diubah dari … ke …").
- Garis `1px --line` di sisi kiri dengan titik kecil kotak (bukan lingkaran berwarna); tanpa avatar besar.

### 6.6 Penanda status
Status **bukan pil berwarna cerah**. Bentuknya: **titik kecil bergaya + teks** pada baris yang sama, tanpa latar penuh.

| Status | Penanda | Warna teks |
|---|---|---|
| Draf | ○ lingkaran kosong | `--slate` |
| Dikonfirmasi / Dipesan / Terbit | ◐ setengah isi | `--ink` |
| Sebagian terkirim / diterima / dibayar | ◑ lebih dari setengah | `--amber` |
| Terkirim / Diterima / Lunas | ● isi penuh | `--moss` |
| Jatuh tempo | ▲ segitiga | `--brick` |
| Batal / Void | ✕ | `--ink-3`, teks dicoret ringan |

- Bentuk dan teks berbeda sehingga status terbaca walau tanpa warna.
- Di tabel, penanda berukuran 8px diikuti teks `--t-small`; pada kepala dokumen sedikit lebih besar.
- Penanda "jatuh tempo" adalah **turunan** (lihat `prd.md` 7.3) dan memunculkan jumlah hari terlambat ("Terlambat 12 hari").

### 6.7 Perintah cepat (Ctrl+K)
- Dialog di tengah atas, lebar 560px. Pencarian lintas dokumen (nomor), produk (SKU/nama), pelanggan, dan tindakan ("Buat pesanan penjualan").
- Hasil dikelompokkan menurut jenis; `↑/↓` memilih, `Enter` membuka, `Esc` menutup.
- Pintasan lain: `g` lalu `s` (ke Penjualan), `g` lalu `p` (Produk), `?` menampilkan lembar pintasan.

### 6.8 Notifikasi dan galat
- **Toast** kecil di kanan bawah untuk keberhasilan tindakan ("SO-2026-000042 dikonfirmasi"); hilang dalam 4 detik, dapat ditutup, tidak menumpuk lebih dari tiga.
- **Galat aturan bisnis** muncul **di tempatnya**: galat `STOK_TIDAK_CUKUP` menandai baris yang bermasalah dengan teks seperti "Tersedia 4, diminta 10" dan tautan ke kartu stok produk.
- Galat jaringan atau server: pita di atas konten dengan penjelasan dan tombol "Coba lagi"; tidak ada halaman putih.
- Galat izin: pesan "Peran Anda (Gudang) tidak dapat menerbitkan faktur", bukan 403 mentah.

### 6.9 Dialog dan panel
- Dialog: radius 6px, latar `--surface`, bayangan mengambang; fokus terkunci di dalamnya; `Esc` menutup; fokus kembali ke pemicu.
- Tindakan berisiko (batal, void) memakai dialog dengan teks yang menyebut dokumen dan akibatnya: "Membatalkan SO-2026-000042 akan melepas reservasi 3 produk."
- Panel samping (riwayat, lampiran) meluncur dari kanan 200ms; tidak menutupi tombol tindakan utama.

### 6.10 Grafik (hanya bila menjawab pertanyaan)
- Laporan memakai tabel sebagai tampilan utama; grafik tambahan hanya untuk dua kasus: **tren penjualan per bulan** (garis) dan **umur piutang** (batang bertumpuk).
- Gaya: garis `1.5px`, sumbu minimal, tanpa kisi tebal, tanpa bayangan, tanpa legenda berlebihan (label langsung pada garis/batang), warna dari token (satu seri `--grain`, seri lain `--ink-3`), angka di sumbu mono.
- Setiap grafik menyertakan tabel datanya (dapat dibuka) agar dapat diakses dan diperiksa.

---

## 7. Keadaan antarmuka

| Keadaan | Perlakuan |
|---|---|
| **Memuat daftar** | Kerangka baris dengan tinggi dan lebar kolom yang sama dengan tabel asli; tanpa putaran spinner di tengah |
| **Memuat dokumen** | Kepala dokumen langsung tampil dari cache bila ada; baris dimuat menyusul |
| **Kosong (belum ada data)** | Satu kalimat dan satu tindakan nyata: "Belum ada pesanan penjualan. Buat yang pertama." Tanpa ilustrasi |
| **Kosong (hasil filter)** | "Tidak ada pesanan yang cocok dengan filter ini." + tautan "Hapus filter" |
| **Galat memuat** | Pita dengan penyebab (jaringan/server) dan tombol "Coba lagi" |
| **Tanpa izin** | Pesan jelas dan tautan kembali; menu yang tidak berhak tidak ditampilkan sama sekali |
| **Server bangun** | Lihat 8 |

---

## 8. Layar "server sedang bangun"

Backend gratis tidur saat sepi (lihat `prd.md` 8.5). Ini bukan galat; ini **keadaan yang dirancang**.

- Muncul bila permintaan pertama lebih dari 3 detik.
- Isi (jujur dan singkat): judul "Server demo sedang bangun", satu paragraf: "Proyek ini berjalan di layanan gratis yang tidur saat tidak dipakai. Biasanya butuh sekitar satu menit." Di bawahnya: garis kemajuan tanpa persentase palsu, lalu waktu berlalu ("12 detik").
- Selagi menunggu, tampilkan **tautan yang bisa dibuka tanpa backend**: diagram arsitektur, ERD, repositori. Waktu tunggu menjadi waktu membaca.
- Ketika server siap, layar menghilang sendiri dan pengguna dikembalikan ke tindakan semula; tidak perlu memuat ulang.
- Indikator kecil di bilah atas ("Server aktif" / "Server bangun…") memberi tahu keadaan tanpa mengganggu.
- Bila lebih dari 90 detik: pesan galat jujur dengan tombol "Coba lagi" dan tautan ke tangkapan layar/video singkat demo yang tersimpan.

---

## 9. Responsif

Aplikasi dirancang untuk desktop, tetapi tetap berguna di perangkat lain.

| Lebar | Perilaku |
|---|---|
| ≥ 1280 | Tata letak penuh; navigasi 220px; panel riwayat berdampingan |
| 1024–1279 | Navigasi dapat diciutkan otomatis; panel riwayat menjadi laci |
| 768–1023 | Navigasi menjadi laci; tabel menggulir ke samping dengan kolom pertama tetap; formulir dua kolom menjadi satu |
| < 768 | **Mode lihat dan tindakan ringan**: daftar berubah menjadi baris bertumpuk (nomor + pihak di atas, status + total di bawah); dokumen menampilkan kepala, baris sebagai daftar, total, dan tombol tindakan; penyuntingan baris besar diarahkan ke layar penuh khusus |

- Sasaran sentuh minimal 44×44px pada ponsel dan tablet.
- Tidak ada fitur yang hanya bisa dicapai dengan hover.
- Penyuntingan tabel lebar di ponsel tidak dipaksakan; pesan jujur menyarankan memakai layar lebih besar untuk menyusun pesanan banyak baris, tetapi persetujuan, pengecekan stok, dan pembayaran tetap nyaman di ponsel.

---

## 10. Halaman pembuka portofolio

Halaman publik di akar situs. Karakternya tenang dan jelas; ia harus bisa dipahami **tanpa backend aktif**.

### 10.1 Susunan

```
┌──────────────────────────────────────────────────────────────┐
│ Lumbung                       Alur · Arsitektur · Kode · Demo│  header
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Sistem pesanan, stok, dan faktur                            │  judul serif besar
│  yang tidak pernah salah hitung.                             │
│                                                              │
│  Mini ERP untuk perusahaan dagang kecil, dibangun dengan     │  pengantar
│  FastAPI, PostgreSQL, dan React. Seluruhnya gratis.          │
│                                                              │
│  [ Coba demo ]   Lihat kode ↗                                │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  [ Diagram alur dokumen: PO → GR → STOK → SO → DO → INV → PAY ]  satu diagram penuh lebar
├──────────────────────────────────────────────────────────────┤
│  Tiga keputusan teknis yang layak dibaca  (kolom teks asimetris)  │
├──────────────────────────────────────────────────────────────┤
│  Coba sebagai:  Admin · Penjualan · Gudang · Keuangan             │  bagian gelap
├──────────────────────────────────────────────────────────────┤
│  Arsitektur & ERD  ·  Catatan jujur  ·  Footer                   │
└──────────────────────────────────────────────────────────────┘
```

### 10.2 Aturan
- **Tidak ada hero foto atau ilustrasi dekoratif.** Elemen visual utamanya adalah **diagram alur dokumen** yang sungguhan, digambar sebagai SVG dari data (lihat 10.3). Karena Lumbung adalah sistem, bukan merek gaya hidup, "gambar" terbaiknya adalah bukti cara kerjanya.
- Judul serif, dua baris, rata kiri, dengan baris kedua boleh menjorok; tidak ada gradien pada teks.
- **Tiga keputusan teknis** disajikan sebagai tiga bagian teks bergantian (teks kiri/diagram kecil kanan), bukan tiga kartu berikon sejajar. Contoh isi: "Buku besar stok yang hanya bertambah", "Uang sebagai bilangan bulat", "Webhook yang aman diulang".
- **Bagian demo:** latar gelap `--paper` mode gelap, empat tombol peran besar. Tiap tombol memuat satu kalimat tentang apa yang bisa dicoba: "Penjualan — buat pesanan dan konfirmasi; lihat stok dipesan secara otomatis."
- **Catatan jujur:** teks pendek tentang batas tier gratis, yang sengaja tidak dibuat, dan rencana berikutnya. Nada: terus terang, bukan apologetik.
- Pemanasan server berjalan diam-diam di latar belakang begitu halaman dibuka (tanpa mengganggu).
- Satu pengungkapan halus saat dimuat: judul naik 8px sambil memudar 500ms. Tidak ada animasi saat menggulir.

### 10.3 Diagram
- Diagram alur dan ERD dibuat sebagai **SVG yang dihasilkan dari definisi data** (satu berkas JSON/TS sumber), agar sinkron dengan skema.
- Gaya: garis `1.5px --ink`, kotak persegi dengan radius 2px, label mono untuk nama tabel, panah tipis, tanpa warna selain `--grain` untuk jalur utama.
- Dapat dibaca di ponsel dengan gulir horizontal terkontrol dan kunci pembesaran; sertakan teks alternatif yang menjelaskan alurnya.

---

## 11. Data contoh (agar tidak terlihat palsu)

Data fiktif seringkali merusak kesan sebuah demo. Aturannya:

- **Perusahaan fiktif satu domain yang konsisten**: distributor bahan bangunan dan perkakas, "UD Sumber Makmur Jaya" (fiktif). Seluruh produk, pelanggan, dan pemasok selaras dengan dunia itu.
- **Produk bernilai dan berukuran masuk akal**: semen 40 kg, paku beton 2", cat tembok 5 kg, pipa PVC ¾", kunci pas set; harga rupiah realistis (bukan angka bulat seragam). SKU berpola (`SMN-040-PC`, `PKU-BTN-2`).
- **Pelanggan fiktif beragam** (toko bangunan, kontraktor, bengkel) dengan termin berbeda (0, 14, 30 hari) dan batas kredit.
- **Riwayat transaksi 90 hari** dengan pola nyata: pesanan lebih banyak di awal bulan, beberapa faktur jatuh tempo, satu-dua pembayaran sebagian, beberapa stok menipis, satu penyesuaian stok karena barang rusak.
- Nama orang dan perusahaan **bukan** nama umum placeholder; tidak memakai orang atau perusahaan sungguhan.
- Seed bersifat **deterministik** (benih tetap) sehingga reset malam selalu menghasilkan keadaan yang sama dan tangkapan layar README tetap sesuai.

---

## 12. Gerak

| Elemen | Perilaku |
|---|---|
| Perubahan status dokumen | Penanda dan stepper berganti dalam 150ms; tanpa animasi besar |
| Toast | Muncul 150ms dari bawah, hilang memudar |
| Dialog dan panel | Memudar 120–200ms |
| Baris baru di tabel | Latar `--grain-wash` yang memudar dalam 1,2 detik untuk menunjukkan "baru" |
| Halaman pembuka | Satu pengungkapan judul 500ms saat dimuat |

Aturan umum: tidak ada animasi yang berulang tanpa henti kecuali indikator menunggu; durasi 120–500ms; semuanya dimatikan oleh `prefers-reduced-motion` (perubahan tetap terjadi, hanya tanpa transisi).

---

## 13. Aksesibilitas

- Kontras diperiksa seperti di 3.3 dan hasilnya disimpan.
- Semua alur utama (membuat SO, mengonfirmasi, mengirim, menerbitkan faktur, mencatat pembayaran) dapat diselesaikan hanya dengan papan ketik.
- Tabel memakai semantik tabel asli (`<table>`, `scope`, `aria-sort`); tabel yang dapat disunting memakai pola `grid` yang terdokumentasi.
- Status tidak hanya dibedakan lewat warna (6.6).
- Galat formulir dikaitkan dengan bidangnya (`aria-describedby`) dan diumumkan ke pembaca layar; fokus pindah ke galat pertama setelah pengiriman gagal.
- Toast diumumkan lewat wilayah `aria-live="polite"`.
- Dialog menjebak fokus dan mengembalikannya.
- Tautan "Lewati ke konten" muncul pertama saat Tab ditekan.
- Sasaran sentuh ≥ 44×44px di perangkat sentuh; ukuran teks minimum 12.5px.
- Diuji dengan pembaca layar pada satu alur penuh sebelum rilis.

---

## 14. Token CSS (acuan implementasi)

```css
:root {
  /* warna */
  --paper:#F7F4EC; --surface:#FFFFFF; --surface-2:#EFEBE0; --surface-hover:#F3EFE4;
  --line:#DDD7C8; --line-strong:#BFB8A5;
  --ink:#1D1C17; --ink-2:#4F4C42; --ink-3:#7A7667;
  --grain:#2F4A3A; --grain-hover:#243A2D; --grain-wash:#E4ECE3;
  --amber:#9A5B13; --amber-wash:#F5E7CF;
  --brick:#A63A2B; --brick-wash:#F6E1DC;
  --moss:#3C6B3F;  --moss-wash:#E1EEDF;
  --slate:#4A5A6A; --slate-wash:#E4E9EE;

  /* tipografi */
  --font-ui:"Public Sans","Helvetica Neue",Arial,sans-serif;
  --font-num:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
  --font-serif:"Newsreader",Georgia,"Times New Roman",serif;
  --t-page:1.375rem; --t-doc:1.25rem; --t-body:.875rem;
  --t-small:.78rem;  --t-total:1.125rem;

  /* ruang & bentuk */
  --row-h:36px; --row-h-dense:30px;
  --radius:4px; --radius-dialog:6px; --radius-tag:2px;
  --shadow-float:0 8px 24px rgba(29,28,23,.14);

  /* gerak */
  --dur-fast:120ms; --dur-base:200ms; --ease:cubic-bezier(.2,.7,.2,1);
}

:root[data-theme="dark"] {
  --paper:#16150F; --surface:#1E1D16; --surface-2:#27261D; --surface-hover:#2B2A21;
  --line:#38362B; --line-strong:#514F40;
  --ink:#EDE9DC; --ink-2:#B8B4A3; --ink-3:#8A8675;
  --grain:#8FBF98; --grain-hover:#A9D2B1; --grain-wash:#223228;
  --amber:#E0A257; --brick:#E3796A; --moss:#83BC86; --slate:#9DB1C4;
  --shadow-float:0 8px 24px rgba(0,0,0,.45);
}

.num { font-family:var(--font-num); font-variant-numeric:tabular-nums; text-align:right; }
.money::before { content:"Rp "; color:var(--ink-3); }

:focus-visible { outline:2px solid var(--grain); outline-offset:2px; border-radius:var(--radius); }

@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{ animation:none !important; transition:none !important; }
}
```

Tailwind (bila dipakai) dikonfigurasi membaca variabel di atas; **tidak ada nilai hex yang ditulis langsung di komponen.**

---

## 15. Daftar periksa tinjauan desain

Setiap layar baru lolos hanya bila semua butir terpenuhi.

- [ ] Tidak ada pola dari daftar larangan di 1.2.
- [ ] Layar punya satu tindakan utama yang jelas (satu tombol `--grain`).
- [ ] Semua angka uang dan jumlah rata kanan, mono, bertabel.
- [ ] Status terbaca tanpa warna (bentuk + teks).
- [ ] Keadaan memuat, kosong, galat, dan tanpa izin sudah dirancang.
- [ ] Alur utama layar bisa diselesaikan dengan papan ketik.
- [ ] Galat aturan bisnis muncul di tempatnya dan menjelaskan apa yang bisa dilakukan.
- [ ] Tidak ada nilai warna, ukuran, atau jarak di luar token.
- [ ] Mode gelap diperiksa satu per satu, bukan hanya dibalik.
- [ ] Diuji pada ponsel nyata untuk alur lihat/setujui/bayar.
- [ ] `prefers-reduced-motion` diuji; layar tetap utuh.
- [ ] Tidak ada data contoh yang tampak palsu atau placeholder generik.
- [ ] Teks antarmuka lugas dan spesifik; tidak ada salinan bergaya SaaS generik.

---

*DESIGN v1.0 — dokumen hidup. Warna dan font adalah titik awal yang beralasan; ubah lewat token, bukan di komponen, dan catat alasannya di `docs/decisions/`.*
