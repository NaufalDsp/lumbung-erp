import React, { useEffect, useState } from "react";
import { api, UserSession } from "./api/client";
import { ColdStartBanner } from "./components/ColdStartBanner";
import { PortfolioHeader } from "./components/PortfolioHeader";
import { DashboardView } from "./pages/DashboardView";
import { LandingPage } from "./pages/LandingPage";
import { PublicPaymentPage } from "./pages/PublicPaymentPage";

export function App() {
  const [currentUser, setCurrentUser] = useState<UserSession | null>(
    api.getCurrentUser(),
  );
  const [activeTab, setActiveTab] = useState<string>("landing");

  useEffect(() => {
    // If no user session exists yet, default to Dewi (Admin) for demo convenience
    if (!currentUser) {
      api
        .demoLogin("admin")
        .then((user) => setCurrentUser(user))
        .catch(() => {
          // If offline or cold start, set demo local fallback
          const fallbackUser: UserSession = {
            id: 1,
            email: "dewi.admin@lumbung.local",
            name: "Dewi Sartika",
            role: "admin",
            is_active: true,
          };
          setCurrentUser(fallbackUser);
        });
    }
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "var(--paper)",
        color: "var(--ink)",
      }}>
      {/* Cold-start detection banner */}
      <ColdStartBanner />

      {/* Portfolio Header with Demo Persona Switcher */}
      <PortfolioHeader
        currentUser={currentUser}
        onUserChange={setCurrentUser}
        onNavigate={setActiveTab}
        activeTab={activeTab}
      />

      {/* Sub Navigation Bar */}
      <div
        style={{
          borderBottom: "1px solid var(--line)",
          backgroundColor: "var(--surface)",
          padding: "0 24px",
        }}>
        <div
          style={{
            maxWidth: "1400px",
            margin: "0 auto",
            display: "flex",
            gap: "24px",
            fontSize: "var(--t-small)",
          }}>
          <button
            onClick={() => setActiveTab("landing")}
            style={{
              padding: "12px 4px",
              border: "none",
              borderBottom:
                activeTab === "landing"
                  ? "2px solid var(--grain)"
                  : "2px solid transparent",
              backgroundColor: "transparent",
              color: activeTab === "landing" ? "var(--grain)" : "var(--ink-2)",
              fontWeight: activeTab === "landing" ? 600 : 400,
              cursor: "pointer",
            }}>
            🏠 Arsitektur & Cerita Produk
          </button>

          <button
            onClick={() => setActiveTab("dashboard")}
            style={{
              padding: "12px 4px",
              border: "none",
              borderBottom:
                activeTab === "dashboard"
                  ? "2px solid var(--grain)"
                  : "2px solid transparent",
              backgroundColor: "transparent",
              color:
                activeTab === "dashboard" ? "var(--grain)" : "var(--ink-2)",
              fontWeight: activeTab === "dashboard" ? 600 : 400,
              cursor: "pointer",
            }}>
            📊 Dashboard Operasional
          </button>

          <button
            onClick={() => setActiveTab("public_invoice")}
            style={{
              padding: "12px 4px",
              border: "none",
              borderBottom:
                activeTab === "public_invoice"
                  ? "2px solid var(--grain)"
                  : "2px solid transparent",
              backgroundColor: "transparent",
              color:
                activeTab === "public_invoice"
                  ? "var(--grain)"
                  : "var(--ink-2)",
              fontWeight: activeTab === "public_invoice" ? 600 : 400,
              cursor: "pointer",
            }}>
            🧾 Simulasi Bayar Faktur (Midtrans Snap)
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <main>
        {activeTab === "landing" && (
          <LandingPage
            onLoginPersona={setCurrentUser}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === "dashboard" && (
          <DashboardView currentUser={currentUser} onNavigate={setActiveTab} />
        )}

        {activeTab === "public_invoice" && (
          <PublicPaymentPage onBackToApp={() => setActiveTab("dashboard")} />
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: "1px solid var(--line)",
          padding: "24px",
          textAlign: "center",
          fontSize: "var(--t-small)",
          color: "var(--ink-3)",
          marginTop: "60px",
        }}>
        <p>
          <strong>Lumbung Mini ERP</strong> • Dibangun dengan prinsip Clean
          Architecture, DDD Taktis, dan Presisi Integer Rupiah.
        </p>
      </footer>
    </div>
  );
}

export default App;
