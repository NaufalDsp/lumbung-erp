import React, { useState } from "react";
import { api, UserSession } from "../api/client";

interface PortfolioHeaderProps {
  currentUser: UserSession | null;
  onUserChange: (user: UserSession | null) => void;
  onNavigate: (tab: string) => void;
  activeTab: string;
}

export const PortfolioHeader: React.FC<PortfolioHeaderProps> = ({
  currentUser,
  onUserChange,
  onNavigate,
  activeTab,
}) => {
  const [loadingRole, setLoadingRole] = useState<string | null>(null);
  const [isResetting, setIsResetting] = useState(false);
  const [isDark, setIsDark] = useState(false);

  const personas = [
    { role: "admin", name: "Dewi", title: "Admin", badge: "Akses Penuh" },
    { role: "sales", name: "Budi", title: "Sales", badge: "SO & Pelanggan" },
    {
      role: "warehouse",
      name: "Siti",
      title: "Gudang",
      badge: "Stok & Surat Jalan",
    },
    { role: "finance", name: "Rudi", title: "Keuangan", badge: "Faktur & Kas" },
  ] as const;

  const handleSwitchPersona = async (
    role: "admin" | "sales" | "warehouse" | "finance",
  ) => {
    try {
      setLoadingRole(role);
      const user = await api.demoLogin(role);
      onUserChange(user);
    } catch (err: any) {
      alert(`Gagal berganti persona: ${err.message}`);
    } finally {
      setLoadingRole(null);
    }
  };

  const handleResetData = async () => {
    const ok = window.confirm(
      "Reset data demo ke kondisi awal deterministik? Tindakan ini akan mengembalikan data master dan transaksi ke data awal.",
    );
    if (!ok) return;

    try {
      setIsResetting(true);
      await api.post("/auth/reset-demo");
      alert("Data demo berhasil di-reset ke kondisi awal!");
      window.location.reload();
    } catch (err: any) {
      alert(`Info: ${err.message || "Endpoint reset demo siap di Fase 9."}`);
    } finally {
      setIsResetting(false);
    }
  };

  const toggleTheme = () => {
    const nextTheme = !isDark;
    setIsDark(nextTheme);
    if (nextTheme) {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  };

  return (
    <header
      style={{
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--line)",
        padding: "12px 24px",
      }}>
      <div
        style={{
          maxWidth: "1400px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
        }}>
        {/* Logo & Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            onClick={() => onNavigate("landing")}
            style={{
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}>
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "var(--radius)",
                backgroundColor: "var(--grain)",
                color: "#FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "1rem",
              }}>
              🌾
            </div>
            <div>
              <span
                style={{
                  fontWeight: 700,
                  fontSize: "1.1rem",
                  color: "var(--ink)",
                }}>
                Lumbung ERP
              </span>
              <span
                style={{
                  marginLeft: "8px",
                  fontSize: "var(--t-small)",
                  color: "var(--ink-3)",
                  borderLeft: "1px solid var(--line)",
                  paddingLeft: "8px",
                }}>
                Mini ERP Sembako
              </span>
            </div>
          </div>

          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "4px 8px",
              borderRadius: "var(--radius-tag)",
              backgroundColor: "var(--moss-wash)",
              color: "var(--moss)",
              fontSize: "0.75rem",
              fontWeight: 600,
            }}>
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: "var(--moss)",
              }}
            />
            PostgreSQL Aktif
          </div>
        </div>

        {/* Persona Switcher Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            flexWrap: "wrap",
          }}>
          <span
            style={{
              fontSize: "var(--t-small)",
              color: "var(--ink-2)",
              fontWeight: 500,
            }}>
            Persona Demo:
          </span>
          <div
            style={{
              display: "flex",
              gap: "4px",
              backgroundColor: "var(--surface-2)",
              padding: "3px",
              borderRadius: "var(--radius)",
            }}>
            {personas.map((p) => {
              const isActive = currentUser?.role === p.role;
              return (
                <button
                  key={p.role}
                  onClick={() => handleSwitchPersona(p.role)}
                  disabled={loadingRole === p.role}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "var(--radius)",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "var(--t-small)",
                    fontWeight: isActive ? 600 : 400,
                    backgroundColor: isActive
                      ? "var(--surface)"
                      : "transparent",
                    color: isActive ? "var(--grain)" : "var(--ink-2)",
                    boxShadow: isActive ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
                    transition: "all var(--dur-fast)",
                  }}
                  title={`${p.name} - ${p.badge}`}>
                  {loadingRole === p.role ? "..." : p.name}
                  <span
                    style={{
                      fontSize: "0.7rem",
                      opacity: 0.7,
                      marginLeft: "4px",
                    }}>
                    ({p.title})
                  </span>
                </button>
              );
            })}
          </div>

          {/* Reset Demo Data Button */}
          <button
            onClick={handleResetData}
            disabled={isResetting}
            title="Kembalikan data transaksi ke data demo awal"
            style={{
              padding: "5px 10px",
              borderRadius: "var(--radius)",
              border: "1px solid var(--line-strong)",
              backgroundColor: "transparent",
              color: "var(--brick)",
              fontSize: "var(--t-small)",
              cursor: "pointer",
            }}>
            {isResetting ? "Reset..." : "↺ Reset Data"}
          </button>

          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            style={{
              padding: "5px 10px",
              borderRadius: "var(--radius)",
              border: "1px solid var(--line)",
              backgroundColor: "transparent",
              cursor: "pointer",
              fontSize: "var(--t-small)",
              color: "var(--ink-2)",
            }}
            title="Ganti Tema">
            {isDark ? "☀️ Terang" : "🌙 Gelap"}
          </button>
        </div>
      </div>
    </header>
  );
};
