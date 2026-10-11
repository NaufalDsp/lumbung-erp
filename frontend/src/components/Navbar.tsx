import React, { useState } from "react";
import {
  BarChart3,
  Boxes,
  History,
  LayoutDashboard,
  LogOut,
  Moon,
  Receipt,
  ShoppingBag,
  ShoppingCart,
  Sun,
} from "lucide-react";
import { UserSession } from "../api/client";
import { Logo } from "./Logo";

interface NavbarProps {
  currentUser: UserSession;
  activeTab: string;
  onNavigate: (tab: string) => void;
  onLogout: () => void;
  onUserChange?: (user: UserSession) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentUser,
  activeTab,
  onNavigate,
  onLogout,
  onUserChange: _onUserChange,
}) => {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    const nextTheme = !isDark;
    setIsDark(nextTheme);
    if (nextTheme) {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  };

  const roleLabels: Record<
    string,
    { label: string; color: string; bg: string }
  > = {
    admin: {
      label: "ADMINISTRATOR",
      color: "var(--grain)",
      bg: "var(--grain-wash)",
    },
    sales: {
      label: "PENJUALAN",
      color: "var(--amber)",
      bg: "var(--amber-wash)",
    },
    warehouse: {
      label: "LOGISTIK GUDANG",
      color: "var(--moss)",
      bg: "var(--moss-wash)",
    },
    finance: {
      label: "KEUANGAN",
      color: "var(--brick)",
      bg: "var(--brick-wash)",
    },
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "inventory", label: "Persediaan", icon: Boxes },
    { id: "purchasing", label: "Pengadaan", icon: ShoppingBag },
    { id: "sales", label: "Penjualan", icon: ShoppingCart },
    { id: "invoicing", label: "Faktur & Kas", icon: Receipt },
    { id: "reports", label: "Laporan", icon: BarChart3 },
    ...(currentUser.role === "admin"
      ? [{ id: "audit", label: "Audit Trail", icon: History }]
      : []),
  ];

  const currentRoleStyle = roleLabels[currentUser.role] || roleLabels.admin;

  return (
    <header
      style={{
        backgroundColor: "var(--surface)",
        borderBottom: "1px solid var(--line)",
        position: "sticky",
        top: 0,
        zIndex: 40,
      }}>
      <div
        style={{
          maxWidth: "1440px",
          margin: "0 auto",
          padding: "0 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          height: "64px",
        }}>
        {/* Left: Brand Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "28px" }}>
          <div
            onClick={() => onNavigate("dashboard")}
            style={{ cursor: "pointer" }}>
            <Logo size="sm" showTagline={false} />
          </div>

          {/* Navigation Items */}
          <nav style={{ display: "flex", gap: "4px" }}>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 12px",
                    borderRadius: "var(--radius)",
                    border: "none",
                    backgroundColor: isActive
                      ? "var(--grain-wash)"
                      : "transparent",
                    color: isActive ? "var(--grain)" : "var(--ink-2)",
                    fontWeight: isActive ? 600 : 500,
                    fontSize: "var(--t-small)",
                    cursor: "pointer",
                    transition: "all var(--dur-fast)",
                  }}>
                  <Icon size={16} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Right: User Profile & Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            style={{
              padding: "6px",
              borderRadius: "var(--radius)",
              border: "1px solid var(--line)",
              backgroundColor: "transparent",
              color: "var(--ink-2)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            title={isDark ? "Tema Terang" : "Tema Gelap"}>
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>

          {/* User Badge */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "4px 8px 4px 12px",
              borderRadius: "var(--radius)",
              backgroundColor: "var(--surface-2)",
              border: "1px solid var(--line)",
            }}>
            <div style={{ textAlign: "right" }}>
              <div
                style={{
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  color: "var(--ink)",
                }}>
                {currentUser.name}
              </div>
              <div
                style={{
                  fontSize: "0.68rem",
                  fontWeight: 700,
                  color: currentRoleStyle.color,
                  letterSpacing: "0.03em",
                }}>
                {currentRoleStyle.label}
              </div>
            </div>

            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                backgroundColor: currentRoleStyle.bg,
                color: currentRoleStyle.color,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "0.75rem",
              }}>
              {currentUser.name.charAt(0)}
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={onLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 12px",
              borderRadius: "var(--radius)",
              border: "1px solid var(--line)",
              backgroundColor: "transparent",
              color: "var(--brick)",
              fontSize: "var(--t-small)",
              fontWeight: 500,
              cursor: "pointer",
            }}
            title="Keluar dari sesi kerja">
            <LogOut size={15} />
            <span className="hidden sm:inline">Keluar</span>
          </button>
        </div>
      </div>
    </header>
  );
};
