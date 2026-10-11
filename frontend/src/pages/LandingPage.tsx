import React from "react";
import { api, UserSession } from "../api/client";

interface LandingPageProps {
  onLoginPersona: (user: UserSession) => void;
  onNavigate: (tab: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onLoginPersona,
  onNavigate,
}) => {
  const handleLaunch = async (
    role: "admin" | "sales" | "warehouse" | "finance",
  ) => {
    try {
      const user = await api.demoLogin(role);
      onLoginPersona(user);
      onNavigate("dashboard");
    } catch (err: any) {
      alert(`Gagal masuk: ${err.message}`);
    }
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "40px 24px" }}>
      {/* Hero Section */}
      <section style={{ textAlign: "center", marginBottom: "56px" }}>
        <div
          style={{
            display: "inline-block",
            padding: "4px 12px",
            borderRadius: "16px",
            backgroundColor: "var(--grain-wash)",
            color: "var(--grain)",
            fontSize: "var(--t-small)",
            fontWeight: 600,
            marginBottom: "16px",
          }}>
          Portfolio Project • Clean Architecture & DDD
        </div>
        <h1
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "2.5rem",
            fontWeight: 700,
            color: "var(--ink)",
            marginBottom: "16px",
            lineHeight: 1.2,
          }}>
          Lumbung Mini ERP
        </h1>
        <p
          style={{
            fontSize: "1.1rem",
            color: "var(--ink-2)",
            maxWidth: "760px",
            margin: "0 auto 32px",
            lineHeight: 1.6,
          }}>
          Sistem operasional distribusi sembako & bahan pangan dengan integritas
          data tinggi. Menghubungkan alur pengadaan pemasok, mutasi stok fisik,
          reservasi pesanan, pengiriman surat jalan, hingga penagihan faktur dan
          pembayaran Midtrans.
        </p>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "12px",
            flexWrap: "wrap",
          }}>
          <button
            onClick={() => handleLaunch("admin")}
            className="btn-primary"
            style={{ padding: "10px 24px", fontSize: "1rem" }}>
            🚀 Masuk Dashboard Demo (Admin)
          </button>
          <button
            onClick={() => onNavigate("public_invoice")}
            className="btn-secondary"
            style={{ padding: "10px 24px", fontSize: "1rem" }}>
            📄 Lihat Simulasi Faktur Publik
          </button>
        </div>
      </section>

      {/* Persona Showcase Grid */}
      <section style={{ marginBottom: "64px" }}>
        <h2
          style={{
            fontSize: "var(--t-doc)",
            fontWeight: 600,
            marginBottom: "20px",
            borderBottom: "1px solid var(--line)",
            paddingBottom: "10px",
          }}>
          Pilih Persona Demo (Role-Based Access Control)
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "20px",
          }}>
          {/* Admin */}
          <div
            style={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}>
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}>
                <h3
                  style={{
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Dewi Sartika
                </h3>
                <span
                  style={{
                    fontSize: "0.75rem",
                    padding: "2px 8px",
                    backgroundColor: "var(--grain-wash)",
                    color: "var(--grain)",
                    borderRadius: "2px",
                    fontWeight: 600,
                  }}>
                  Admin
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                }}>
                Memiliki hak akses penuh untuk mengelola master data, audit
                trail, pemicu alert Telegram, dan reset sistem.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("admin")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Buka sebagai Dewi
            </button>
          </div>

          {/* Sales */}
          <div
            style={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}>
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}>
                <h3
                  style={{
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Budi Santoso
                </h3>
                <span
                  style={{
                    fontSize: "0.75rem",
                    padding: "2px 8px",
                    backgroundColor: "var(--amber-wash)",
                    color: "var(--amber)",
                    borderRadius: "2px",
                    fontWeight: 600,
                  }}>
                  Sales
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                }}>
                Fokus pada input Pesanan Penjualan (SO), pemantauan kuota limit
                kredit pelanggan, dan status pengiriman.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("sales")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Buka sebagai Budi
            </button>
          </div>

          {/* Warehouse */}
          <div
            style={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}>
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}>
                <h3
                  style={{
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Siti Rahayu
                </h3>
                <span
                  style={{
                    fontSize: "0.75rem",
                    padding: "2px 8px",
                    backgroundColor: "var(--moss-wash)",
                    color: "var(--moss)",
                    borderRadius: "2px",
                    fontWeight: 600,
                  }}>
                  Gudang
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                }}>
                Mencatat penerimaan barang (Goods Receipt) dari pemasok, opname
                stok, dan penerbitan Surat Jalan (DO).
              </p>
            </div>
            <button
              onClick={() => handleLaunch("warehouse")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Buka sebagai Siti
            </button>
          </div>

          {/* Finance */}
          <div
            style={{
              backgroundColor: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}>
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "8px",
                }}>
                <h3
                  style={{
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Rudi Hermawan
                </h3>
                <span
                  style={{
                    fontSize: "0.75rem",
                    padding: "2px 8px",
                    backgroundColor: "var(--brick-wash)",
                    color: "var(--brick)",
                    borderRadius: "2px",
                    fontWeight: 600,
                  }}>
                  Keuangan
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                }}>
                Menerbitkan Faktur (Invoice), memvalidasi pembayaran
                transfer/Midtrans, serta memantau Laporan Umur Piutang.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("finance")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Buka sebagai Rudi
            </button>
          </div>
        </div>
      </section>

      {/* Engineering Highlights */}
      <section>
        <h2
          style={{
            fontSize: "var(--t-doc)",
            fontWeight: 600,
            marginBottom: "20px",
            borderBottom: "1px solid var(--line)",
            paddingBottom: "10px",
          }}>
          Prinsip Rekayasa Perangkat Lunak & Clean Architecture
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: "20px",
          }}>
          <div
            style={{
              backgroundColor: "var(--surface)",
              padding: "20px",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
            }}>
            <h4
              style={{
                fontWeight: 600,
                marginBottom: "8px",
                color: "var(--grain)",
              }}>
              🎯 Zero-Float Integer Currency & Tax
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Semua kalkulasi nilai uang disimpan dalam integer Rupiah. Diskon
              dan PPN 11% dikalkulasi dengan basis points (1100 bp) menggunakan
              pembulatan Half-Up integer, menjamin tidak ada pembulatan
              mengambang (float drift).
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--surface)",
              padding: "20px",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
            }}>
            <h4
              style={{
                fontWeight: 600,
                marginBottom: "8px",
                color: "var(--grain)",
              }}>
              🔒 Buku Besar Stok & Concurrency-Safe
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Tabel buku besar <code>stock_moves</code> append-only menjamin
              jejak audit tak terbantahkan. Pengecekan saldo memanfaatkan{" "}
              <code>SELECT ... FOR UPDATE</code> dan constraint PostgreSQL{" "}
              <code>CHECK (on_hand &gt;= 0)</code>.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--surface)",
              padding: "20px",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
            }}>
            <h4
              style={{
                fontWeight: 600,
                marginBottom: "8px",
                color: "var(--grain)",
              }}>
              ⚡ Integrasi Midtrans & Webhook Idempoten
            </h4>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Tautan pembayaran publik acak 128-bit dengan verifikasi tanda
              tangan SHA-512 constant-time. Tabel <code>webhook_events</code>{" "}
              memastikan setiap notifikasi pembayaran diproses tepat satu kali
              (exactly-once processing).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
