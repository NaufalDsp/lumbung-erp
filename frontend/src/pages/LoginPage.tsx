import React, { useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Lock,
  Mail,
  Shield,
} from "lucide-react";
import { api, UserSession } from "../api/client";
import { Logo } from "../components/Logo";

interface LoginPageProps {
  onLoginSuccess: (user: UserSession) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("dewi.sartika@lumbungpangan.co.id");
  const [password, setPassword] = useState("Lumbung2026!");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage("Mohon masukkan email dan kata sandi perusahaan Anda.");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage(null);
      const user = await api.login(email, password);
      onLoginSuccess(user);
    } catch (err: any) {
      setErrorMessage(err.message || "Gagal masuk ke sistem.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPreload = (userEmail: string) => {
    setEmail(userEmail);
    setPassword("Lumbung2026!");
    setErrorMessage(null);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        backgroundColor: "var(--paper)",
        color: "var(--ink)",
      }}>
      {/* Left Column: Corporate Brand Showcase */}
      <div
        style={{
          flex: "1 1 50%",
          padding: "60px 48px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          backgroundColor: "var(--grain)",
          color: "#FFFFFF",
          position: "relative",
          overflow: "hidden",
        }}
        className="hidden md:flex">
        <div>
          <div
            style={{ filter: "brightness(0) invert(1)", marginBottom: "48px" }}>
            <Logo size="lg" showTagline={false} />
          </div>

          <h1
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "2.75rem",
              lineHeight: 1.2,
              fontWeight: 600,
              marginBottom: "24px",
              color: "#FFFFFF",
            }}>
            Sistem Tata Kelola Distribusi Komoditas Pangan
          </h1>

          <p
            style={{
              fontSize: "1.05rem",
              lineHeight: 1.6,
              color: "rgba(255, 255, 255, 0.85)",
              maxWidth: "520px",
              marginBottom: "36px",
            }}>
            Platform operasional menyeluruh untuk pengadaan pemasok, pencatatan
            mutasi stok fisik, pemenuhan pesanan penjualan, dan penerbitan
            faktur tagihan resmi.
          </p>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "16px",
              maxWidth: "480px",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
              }}>
              <CheckCircle2
                size={20}
                color="#8FBF98"
                style={{ flexShrink: 0, marginTop: "2px" }}
              />
              <span
                style={{
                  fontSize: "0.9rem",
                  color: "rgba(255, 255, 255, 0.9)",
                }}>
                Integritas buku besar stok persediaan (inventory ledger)
                append-only dengan kalkulasi HPP Moving Average.
              </span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
              }}>
              <CheckCircle2
                size={20}
                color="#8FBF98"
                style={{ flexShrink: 0, marginTop: "2px" }}
              />
              <span
                style={{
                  fontSize: "0.9rem",
                  color: "rgba(255, 255, 255, 0.9)",
                }}>
                Perhitungan presisi integer Rupiah tanpa pembulatan mengambang
                (zero float drift).
              </span>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
              }}>
              <CheckCircle2
                size={20}
                color="#8FBF98"
                style={{ flexShrink: 0, marginTop: "2px" }}
              />
              <span
                style={{
                  fontSize: "0.9rem",
                  color: "rgba(255, 255, 255, 0.9)",
                }}>
                Otorisasi peran berjenjang (RBAC) teruji: Direksi, Penjualan,
                Logistik Gudang, dan Keuangan.
              </span>
            </div>
          </div>
        </div>

        <div
          style={{
            fontSize: "0.8rem",
            color: "rgba(255, 255, 255, 0.6)",
            borderTop: "1px solid rgba(255, 255, 255, 0.15)",
            paddingTop: "20px",
          }}>
          PT Lumbung Pangan Nusantara • Enterprise Resource Planning v0.1.0
        </div>
      </div>

      {/* Right Column: Secure Login Form */}
      <div
        style={{
          flex: "1 1 50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "32px 24px",
        }}>
        <div style={{ width: "100%", maxWidth: "420px" }}>
          <div style={{ marginBottom: "32px" }}>
            <Logo size="md" />
            <h2
              style={{
                fontSize: "1.5rem",
                fontWeight: 700,
                marginTop: "24px",
                marginBottom: "8px",
                color: "var(--ink)",
              }}>
              Masuk ke Portal Perusahaan
            </h2>
            <p style={{ fontSize: "var(--t-small)", color: "var(--ink-2)" }}>
              Silakan masukkan kredensial resmi akun perusahaan Anda.
            </p>
          </div>

          {errorMessage && (
            <div
              style={{
                backgroundColor: "var(--brick-wash)",
                border: "1px solid var(--brick)",
                borderRadius: "var(--radius)",
                padding: "12px 14px",
                marginBottom: "20px",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                fontSize: "var(--t-small)",
                color: "var(--brick)",
              }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{errorMessage}</span>
            </div>
          )}

          <form
            onSubmit={handleLogin}
            style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: "var(--t-small)",
                  fontWeight: 600,
                  color: "var(--ink-2)",
                  marginBottom: "6px",
                }}>
                Alamat Email Perusahaan
              </label>
              <div style={{ position: "relative" }}>
                <Mail
                  size={16}
                  style={{
                    position: "absolute",
                    left: "12px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "var(--ink-3)",
                  }}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="nama@lumbungpangan.co.id"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px 9px 38px",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--line-strong)",
                    backgroundColor: "var(--surface)",
                    color: "var(--ink)",
                    fontSize: "var(--t-body)",
                    outline: "none",
                  }}
                />
              </div>
            </div>

            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "6px",
                }}>
                <label
                  style={{
                    fontSize: "var(--t-small)",
                    fontWeight: 600,
                    color: "var(--ink-2)",
                  }}>
                  Kata Sandi
                </label>
                <span style={{ fontSize: "0.75rem", color: "var(--ink-3)" }}>
                  Standar Keamanan Argon2id
                </span>
              </div>
              <div style={{ position: "relative" }}>
                <Lock
                  size={16}
                  style={{
                    position: "absolute",
                    left: "12px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    color: "var(--ink-3)",
                  }}
                />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  style={{
                    width: "100%",
                    padding: "9px 12px 9px 38px",
                    borderRadius: "var(--radius)",
                    border: "1px solid var(--line-strong)",
                    backgroundColor: "var(--surface)",
                    color: "var(--ink)",
                    fontSize: "var(--t-body)",
                    outline: "none",
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{
                width: "100%",
                padding: "10px",
                fontSize: "0.95rem",
                fontWeight: 600,
                marginTop: "6px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: "8px",
              }}>
              {isLoading ? "Mengautentikasi..." : "Masuk ke Sistem"}
              {!isLoading && <ArrowRight size={16} />}
            </button>
          </form>

          {/* Enterprise Accounts Quick Selector */}
          <div
            style={{
              marginTop: "32px",
              paddingTop: "24px",
              borderTop: "1px solid var(--line)",
            }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "12px",
              }}>
              <Shield size={16} color="var(--grain)" />
              <span
                style={{
                  fontSize: "0.8rem",
                  fontWeight: 600,
                  color: "var(--ink-2)",
                }}>
                Akun Pegawai Resmi (Kredensial Default):
              </span>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "8px",
              }}>
              <button
                type="button"
                onClick={() =>
                  handleSelectPreload("dewi.sartika@lumbungpangan.co.id")
                }
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--line)",
                  backgroundColor: "var(--surface)",
                  cursor: "pointer",
                }}>
                <div
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Dewi Sartika
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--grain)" }}>
                  Administrator
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  handleSelectPreload("budi.santoso@lumbungpangan.co.id")
                }
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--line)",
                  backgroundColor: "var(--surface)",
                  cursor: "pointer",
                }}>
                <div
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Budi Santoso
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--amber)" }}>
                  Staff Penjualan
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  handleSelectPreload("siti.rahayu@lumbungpangan.co.id")
                }
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--line)",
                  backgroundColor: "var(--surface)",
                  cursor: "pointer",
                }}>
                <div
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Siti Rahayu
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--moss)" }}>
                  Kepala Gudang
                </div>
              </button>

              <button
                type="button"
                onClick={() =>
                  handleSelectPreload("rudi.hermawan@lumbungpangan.co.id")
                }
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--line)",
                  backgroundColor: "var(--surface)",
                  cursor: "pointer",
                }}>
                <div
                  style={{
                    fontSize: "0.78rem",
                    fontWeight: 600,
                    color: "var(--ink)",
                  }}>
                  Rudi Hermawan
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--brick)" }}>
                  Staff Keuangan
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
