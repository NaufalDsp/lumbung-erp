import React, { useEffect, useState } from "react";
import { api, UserSession } from "../api/client";
import { formatRupiah, formatNumber } from "../lib/formatters";

interface DashboardViewProps {
  currentUser: UserSession | null;
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  currentUser,
  onNavigate,
}) => {
  const [stats, setStats] = useState({
    stockValuation: 184500000,
    skuCount: 48,
    lowStockCount: 3,
    salesRevenue: 64200000,
    totalAr: 18750000,
  });

  const [loading, setLoading] = useState(false);

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
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "32px 24px" }}>
      {/* Welcome Banner */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "28px",
        }}>
        <div>
          <h1
            style={{
              fontSize: "1.75rem",
              fontWeight: 700,
              color: "var(--ink)",
            }}>
            Selamat Datang, {currentUser?.name || "Pengguna Demo"}
          </h1>
          <p style={{ color: "var(--ink-2)", fontSize: "var(--t-small)" }}>
            Role Aktif:{" "}
            <strong
              style={{ color: "var(--grain)", textTransform: "uppercase" }}>
              {currentUser?.role || "Admin"}
            </strong>{" "}
            • Lumbung Pangan Nusantara
          </p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() => onNavigate("reports")}
            className="btn-secondary">
            📊 Buka Laporan
          </button>
          <button
            onClick={() => onNavigate("landing")}
            className="btn-secondary">
            📖 Ringkasan Arsitektur
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "16px",
          marginBottom: "36px",
        }}>
        {/* KPI 1: Nilai Aset Stok */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <span
            style={{
              fontSize: "var(--t-small)",
              color: "var(--ink-3)",
              fontWeight: 500,
            }}>
            Total Valuasi Stok (HPP)
          </span>
          <div
            className="num"
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "var(--ink)",
              margin: "8px 0",
              textAlign: "left",
            }}>
            {formatRupiah(stats.stockValuation)}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--moss)" }}>
            ● Berdasarkan Moving Average Cost
          </span>
        </div>

        {/* KPI 2: Total SKU */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <span
            style={{
              fontSize: "var(--t-small)",
              color: "var(--ink-3)",
              fontWeight: 500,
            }}>
            Total SKU Aktif
          </span>
          <div
            className="num"
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "var(--ink)",
              margin: "8px 0",
              textAlign: "left",
            }}>
            {formatNumber(stats.skuCount)} Produk
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--grain)" }}>
            Beras, Minyak, Gula, Tepung
          </span>
        </div>

        {/* KPI 3: Stok Menipis */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <span
            style={{
              fontSize: "var(--t-small)",
              color: "var(--ink-3)",
              fontWeight: 500,
            }}>
            Peringatan Stok Menipis
          </span>
          <div
            className="num"
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "var(--brick)",
              margin: "8px 0",
              textAlign: "left",
            }}>
            {stats.lowStockCount} SKU
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--brick)" }}>
            Di bawah batas minimum stok
          </span>
        </div>

        {/* KPI 4: Piutang Pelanggan */}
        <div
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "20px",
          }}>
          <span
            style={{
              fontSize: "var(--t-small)",
              color: "var(--ink-3)",
              fontWeight: 500,
            }}>
            Total Piutang Berjalan (AR)
          </span>
          <div
            className="num"
            style={{
              fontSize: "1.5rem",
              fontWeight: 700,
              color: "var(--amber)",
              margin: "8px 0",
              textAlign: "left",
            }}>
            {formatRupiah(stats.totalAr)}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--amber)" }}>
            Faktur Terbit & Sebagian Bayar
          </span>
        </div>
      </div>

      {/* Quick Operational Shortcuts */}
      <section
        style={{
          backgroundColor: "var(--surface)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius)",
          padding: "24px",
          marginBottom: "32px",
        }}>
        <h2
          style={{
            fontSize: "var(--t-doc)",
            fontWeight: 600,
            marginBottom: "16px",
            color: "var(--ink)",
          }}>
          Alur Operasional Inti
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "16px",
          }}>
          <div
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
            }}>
            <h4 style={{ fontWeight: 600, marginBottom: "6px" }}>
              1. Pengadaan (PO)
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                marginBottom: "12px",
              }}>
              Pesan pasokan bahan pangan ke pemasok terdaftar.
            </p>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              Kode: PO-YYYY-XXXXXX
            </span>
          </div>

          <div
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
            }}>
            <h4 style={{ fontWeight: 600, marginBottom: "6px" }}>
              2. Penerimaan (GR)
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                marginBottom: "12px",
              }}>
              Barang tiba di gudang, mutasi stok fisik bertambah.
            </p>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              Kode: GR-YYYY-XXXXXX
            </span>
          </div>

          <div
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
            }}>
            <h4 style={{ fontWeight: 600, marginBottom: "6px" }}>
              3. Pesanan Sales (SO)
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                marginBottom: "12px",
              }}>
              Pesanan pelanggan, stok otomatis direservasi.
            </p>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              Kode: SO-YYYY-XXXXXX
            </span>
          </div>

          <div
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
            }}>
            <h4 style={{ fontWeight: 600, marginBottom: "6px" }}>
              4. Pengiriman (DO)
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                marginBottom: "12px",
              }}>
              Penerbitan surat jalan, deduksi stok on-hand & reserved.
            </p>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              Kode: DO-YYYY-XXXXXX
            </span>
          </div>

          <div
            style={{
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "16px",
            }}>
            <h4 style={{ fontWeight: 600, marginBottom: "6px" }}>
              5. Faktur & Bayar (INV)
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                marginBottom: "12px",
              }}>
              Faktur PPN 11% integer, tautan bayar Midtrans Snap.
            </p>
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--grain)",
                fontWeight: 600,
              }}>
              Kode: INV-YYYY-XXXXXX
            </span>
          </div>
        </div>
      </section>
    </div>
  );
};
