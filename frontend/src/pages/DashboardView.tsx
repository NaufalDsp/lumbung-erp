import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  Boxes,
  Building2,
  CheckCircle2,
  CreditCard,
  FileText,
  Package,
  Receipt,
  ShoppingBag,
  ShoppingCart,
  Truck,
} from "lucide-react";
import { api, UserSession } from "../api/client";
import { formatNumber, formatRupiah } from "../lib/formatters";

interface DashboardViewProps {
  currentUser: UserSession;
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  currentUser,
  onNavigate,
}) => {
  const [stats, setStats] = useState({
    stockValuation: 184500000,
    skuCount: 6,
    lowStockCount: 0,
    salesRevenue: 4867250,
    totalAr: 2453100,
  });

  const [_loading, setLoading] = useState(false);

  useEffect(() => {
    // Optionally fetch live report stats from backend if token exists
    const loadStats = async () => {
      try {
        setLoading(true);
        const [valReport, arReport] = await Promise.allSettled([
          api.get("/reports/stock-valuation"),
          api.get("/reports/ar-aging"),
        ]);

        if (valReport.status === "fulfilled" && valReport.value) {
          setStats((prev) => ({
            ...prev,
            stockValuation:
              valReport.value.total_asset_value || prev.stockValuation,
            skuCount: valReport.value.total_sku_count || prev.skuCount,
          }));
        }

        if (arReport.status === "fulfilled" && arReport.value) {
          setStats((prev) => ({
            ...prev,
            totalAr: arReport.value.total_ar || prev.totalAr,
          }));
        }
      } catch {
        // Fallback to sample stats on local preview
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [currentUser]);

  return (
    <div style={{ maxWidth: "1440px", margin: "0 auto", padding: "28px 24px" }}>
      {/* Top Banner & Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          marginBottom: "28px",
          borderBottom: "1px solid var(--line)",
          paddingBottom: "18px",
        }}>
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "4px",
            }}>
            <Building2 size={18} color="var(--grain)" />
            <span
              style={{
                fontSize: "0.85rem",
                fontWeight: 600,
                color: "var(--ink-3)",
              }}>
              PT LUMBUNG PANGAN NUSANTARA • PUSAT OPERASIONAL
            </span>
          </div>
          <h1
            style={{
              fontSize: "1.65rem",
              fontWeight: 700,
              color: "var(--ink)",
            }}>
            Ringkasan Eksekutif & Operasional
          </h1>
          <p
            style={{
              color: "var(--ink-2)",
              fontSize: "var(--t-small)",
              marginTop: "2px",
            }}>
            Selamat datang, <strong>{currentUser?.name || "Karyawan"}</strong> •
            Jabatan:{" "}
            <span
              style={{
                textTransform: "uppercase",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              {currentUser?.role || "Pengguna"}
            </span>
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() => onNavigate("reports")}
            className="btn-secondary"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <FileText size={15} />
            <span>Laporan Lengkap</span>
          </button>
          <button
            onClick={() => onNavigate("sales")}
            className="btn-primary"
            style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <ShoppingCart size={15} />
            <span>Entri Pesanan Baru</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "18px",
          marginBottom: "32px",
        }}>
        {/* KPI 1: Nilai Aset Stok */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "12px",
            }}>
            <span
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
                fontWeight: 600,
              }}>
              TOTAL VALUASI PERSEDIAAN
            </span>
            <div
              style={{
                padding: "6px",
                backgroundColor: "var(--grain-wash)",
                borderRadius: "var(--radius-tag)",
              }}>
              <Boxes size={18} color="var(--grain)" />
            </div>
          </div>
          <div
            className="num"
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              color: "var(--ink)",
              textAlign: "left",
              marginBottom: "6px",
            }}>
            {formatRupiah(stats.stockValuation)}
          </div>
          <div
            style={{
              fontSize: "0.75rem",
              color: "var(--moss)",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}>
            <CheckCircle2 size={13} />
            <span>Moving Average Cost (Buku Besar Akurat)</span>
          </div>
        </div>

        {/* KPI 2: Total SKU Aktif */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "12px",
            }}>
            <span
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
                fontWeight: 600,
              }}>
              TOTAL SKU KOMODITAS AKTIF
            </span>
            <div
              style={{
                padding: "6px",
                backgroundColor: "var(--moss-wash)",
                borderRadius: "var(--radius-tag)",
              }}>
              <Package size={18} color="var(--moss)" />
            </div>
          </div>
          <div
            className="num"
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              color: "var(--ink)",
              textAlign: "left",
              marginBottom: "6px",
            }}>
            {formatNumber(stats.skuCount)} Produk
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--ink-3)" }}>
            Beras Premium, Minyak Goreng, Gula Pasir, Terigu
          </div>
        </div>

        {/* KPI 3: Status Stok Kritis */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "12px",
            }}>
            <span
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
                fontWeight: 600,
              }}>
              PERINGATAN STOK MINIMUM
            </span>
            <div
              style={{
                padding: "6px",
                backgroundColor:
                  stats.lowStockCount > 0
                    ? "var(--brick-wash)"
                    : "var(--moss-wash)",
                borderRadius: "var(--radius-tag)",
              }}>
              <AlertTriangle
                size={18}
                color={stats.lowStockCount > 0 ? "var(--brick)" : "var(--moss)"}
              />
            </div>
          </div>
          <div
            className="num"
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              color: stats.lowStockCount > 0 ? "var(--brick)" : "var(--moss)",
              textAlign: "left",
              marginBottom: "6px",
            }}>
            {stats.lowStockCount} SKU
          </div>
          <div
            style={{
              fontSize: "0.75rem",
              color: stats.lowStockCount > 0 ? "var(--brick)" : "var(--moss)",
            }}>
            {stats.lowStockCount > 0
              ? "Memerlukan penerbitan PO mendesak"
              : "Kapasitas gudang dalam batas aman"}
          </div>
        </div>

        {/* KPI 4: Piutang Berjalan */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "12px",
            }}>
            <span
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
                fontWeight: 600,
              }}>
              TOTAL PIUTANG USAHA (AR)
            </span>
            <div
              style={{
                padding: "6px",
                backgroundColor: "var(--amber-wash)",
                borderRadius: "var(--radius-tag)",
              }}>
              <CreditCard size={18} color="var(--amber)" />
            </div>
          </div>
          <div
            className="num"
            style={{
              fontSize: "1.6rem",
              fontWeight: 700,
              color: "var(--amber)",
              textAlign: "left",
              marginBottom: "6px",
            }}>
            {formatRupiah(stats.totalAr)}
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--amber)" }}>
            Termin 14 - 30 hari kalender
          </div>
        </div>
      </div>

      {/* Main Workflow Stages */}
      <section
        style={{
          backgroundColor: "var(--surface)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius)",
          padding: "24px",
          marginBottom: "32px",
        }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "18px",
          }}>
          <div>
            <h2
              style={{
                fontSize: "var(--t-doc)",
                fontWeight: 600,
                color: "var(--ink)",
              }}>
              Alur Transaksi & Rantai Pasok Terpadu
            </h2>
            <p style={{ fontSize: "var(--t-small)", color: "var(--ink-3)" }}>
              Siklus dokumen berurutan dari pembelian hingga pelunasan
              pembayaran dengan jaminan integritas data.
            </p>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
            gap: "14px",
          }}>
          <div
            onClick={() => onNavigate("purchasing")}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
              cursor: "pointer",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <ShoppingBag size={18} color="var(--grain)" />
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                1. Pengadaan (PO)
              </span>
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--ink-2)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}>
              Penerbitan surat pesanan ke pemasok pangan terdaftar.
            </p>
            <span
              style={{
                fontSize: "0.7rem",
                fontFamily: "var(--font-num)",
                color: "var(--ink-3)",
              }}>
              Format: PO-YYYY-XXXXXX
            </span>
          </div>

          <div
            onClick={() => onNavigate("inventory")}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
              cursor: "pointer",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <Boxes size={18} color="var(--moss)" />
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                2. Penerimaan (GR)
              </span>
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--ink-2)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}>
              Penerimaan fisik gudang, mutasi stok masuk, dan pembaruan HPP.
            </p>
            <span
              style={{
                fontSize: "0.7rem",
                fontFamily: "var(--font-num)",
                color: "var(--ink-3)",
              }}>
              Format: GR-YYYY-XXXXXX
            </span>
          </div>

          <div
            onClick={() => onNavigate("sales")}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
              cursor: "pointer",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <ShoppingCart size={18} color="var(--amber)" />
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                3. Penjualan (SO)
              </span>
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--ink-2)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}>
              Pemesanan distributor / retail dengan reservasi stok otomatis.
            </p>
            <span
              style={{
                fontSize: "0.7rem",
                fontFamily: "var(--font-num)",
                color: "var(--ink-3)",
              }}>
              Format: SO-YYYY-XXXXXX
            </span>
          </div>

          <div
            onClick={() => onNavigate("sales")}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
              cursor: "pointer",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <Truck size={18} color="var(--slate)" />
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                4. Pengiriman (DO)
              </span>
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--ink-2)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}>
              Surat jalan armada logistik, pemotongan stok on-hand & reservasi.
            </p>
            <span
              style={{
                fontSize: "0.7rem",
                fontFamily: "var(--font-num)",
                color: "var(--ink-3)",
              }}>
              Format: DO-YYYY-XXXXXX
            </span>
          </div>

          <div
            onClick={() => onNavigate("invoicing")}
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
              cursor: "pointer",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <Receipt size={18} color="var(--brick)" />
              <span style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                5. Faktur & Bayar
              </span>
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--ink-2)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}>
              Penagihan PPN 11% integer, pelunasan transfer bank & Midtrans.
            </p>
            <span
              style={{
                fontSize: "0.7rem",
                fontFamily: "var(--font-num)",
                color: "var(--ink-3)",
              }}>
              Format: INV-YYYY-XXXXXX
            </span>
          </div>
        </div>
      </section>
    </div>
  );
};
