import React from "react";
import {
  ArrowRight,
  Building2,
  Cpu,
  CreditCard,
  Database,
  FileCode2,
  ShieldCheck,
  UserCheck,
} from "lucide-react";
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
      const user = await api.switchRole(role);
      onLoginPersona(user);
      onNavigate("dashboard");
    } catch (err: any) {
      alert(`Gagal masuk: ${err.message}`);
    }
  };

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "40px 24px" }}>
      {/* Hero Section */}
      <section style={{ textAlign: "center", marginBottom: "56px" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "4px 14px",
            borderRadius: "16px",
            backgroundColor: "var(--grain-wash)",
            color: "var(--grain)",
            fontSize: "var(--t-small)",
            fontWeight: 600,
            marginBottom: "16px",
          }}>
          <Building2 size={15} />
          <span>PT Lumbung Pangan Nusantara • Sistem Informasi Enterprise</span>
        </div>
        <h1
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "2.6rem",
            fontWeight: 700,
            color: "var(--ink)",
            marginBottom: "16px",
            lineHeight: 1.2,
          }}>
          Lumbung Enterprise Resource Planning
        </h1>
        <p
          style={{
            fontSize: "1.05rem",
            color: "var(--ink-2)",
            maxWidth: "780px",
            margin: "0 auto 32px",
            lineHeight: 1.6,
          }}>
          Platform terpadu rantai pasok dan operasional komoditas pangan
          nasional. Menyediakan jaminan integritas data dari pengadaan barang
          pemasok, penelusuran buku besar mutasi gudang, reservasi pesanan
          penjualan, hingga penagihan faktur resmi.
        </p>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "14px",
            flexWrap: "wrap",
          }}>
          <button
            onClick={() => onNavigate("dashboard")}
            className="btn-primary"
            style={{
              padding: "10px 24px",
              fontSize: "0.95rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}>
            <span>Buka Dashboard Operasional</span>
            <ArrowRight size={16} />
          </button>
          <button
            onClick={() => onNavigate("public_invoice")}
            className="btn-secondary"
            style={{
              padding: "10px 24px",
              fontSize: "0.95rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}>
            <CreditCard size={16} />
            <span>Portal Pembayaran Faktur</span>
          </button>
        </div>
      </section>

      {/* Corporate Division Access Grid */}
      <section style={{ marginBottom: "64px" }}>
        <h2
          style={{
            fontSize: "var(--t-doc)",
            fontWeight: 600,
            marginBottom: "20px",
            borderBottom: "1px solid var(--line)",
            paddingBottom: "10px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}>
          <UserCheck size={20} color="var(--grain)" />
          <span>
            Akses Cepat Divisi Operasional (Role-Based Access Control)
          </span>
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
                    fontSize: "1.05rem",
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
                  Administrator
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                  lineHeight: 1.45,
                }}>
                Akses tata kelola master data, jejak audit (audit trail),
                konfigurasi sistem, dan integrasi notifikasi operasional.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("admin")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Masuk sebagai Administrator
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
                    fontSize: "1.05rem",
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
                  Penjualan (Sales)
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                  lineHeight: 1.45,
                }}>
                Pengelolaan Pesanan Penjualan (SO), monitoring batas kredit
                pelanggan, dan koordinasi alokasi kuota komoditas.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("sales")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Masuk sebagai Penjualan
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
                    fontSize: "1.05rem",
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
                  Logistik & Gudang
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                  lineHeight: 1.45,
                }}>
                Pencatatan penerimaan barang (Goods Receipt), opname persediaan,
                dan penerbitan Surat Jalan (Delivery Order).
              </p>
            </div>
            <button
              onClick={() => handleLaunch("warehouse")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Masuk sebagai Gudang
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
                    fontSize: "1.05rem",
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
                  Keuangan (Finance)
                </span>
              </div>
              <p
                style={{
                  fontSize: "var(--t-small)",
                  color: "var(--ink-2)",
                  marginBottom: "16px",
                  lineHeight: 1.45,
                }}>
                Penerbitan faktur pajak/komersial resmi, rekonsiliasi pembayaran
                perbankan, dan monitoring laporan umur piutang.
              </p>
            </div>
            <button
              onClick={() => handleLaunch("finance")}
              className="btn-secondary"
              style={{ width: "100%" }}>
              Masuk sebagai Keuangan
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
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}>
          <Cpu size={20} color="var(--grain)" />
          <span>Prinsip Keandalan Arsitektur Perangkat Lunak Enterprise</span>
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
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <FileCode2 size={18} color="var(--grain)" />
              <h4 style={{ fontWeight: 600, color: "var(--grain)" }}>
                Zero-Float Integer Currency & Tax
              </h4>
            </div>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Semua nilai finansial disimpan dalam integer Rupiah. Diskon dan
              PPN 11% dikalkulasi dengan basis points (1100 bp) menggunakan
              algoritma pembulatan Half-Up integer, menjamin nihil deviasi
              desimal.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--surface)",
              padding: "20px",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <Database size={18} color="var(--moss)" />
              <h4 style={{ fontWeight: 600, color: "var(--moss)" }}>
                Buku Besar Stok & Concurrency-Safe
              </h4>
            </div>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Tabel buku besar <code>stock_moves</code> bersifat append-only.
              Verifikasi saldo menggunakan <code>SELECT ... FOR UPDATE</code>{" "}
              serta constraint database <code>CHECK (on_hand &gt;= 0)</code>.
            </p>
          </div>

          <div
            style={{
              backgroundColor: "var(--surface)",
              padding: "20px",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius)",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
              }}>
              <ShieldCheck size={18} color="var(--amber)" />
              <h4 style={{ fontWeight: 600, color: "var(--amber)" }}>
                Integrasi Pembayaran Idempoten
              </h4>
            </div>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-2)",
                lineHeight: 1.5,
              }}>
              Token faktur 128-bit dengan validasi tanda tangan SHA-512
              constant-time. Tabel <code>webhook_events</code> menjamin
              pemrosesan mutasi pembayaran tepat satu kali (exactly-once
              processing).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
