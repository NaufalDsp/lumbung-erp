import { useState } from "react";
import { api, UserSession } from "./api/client";
import { ColdStartBanner } from "./components/ColdStartBanner";
import { Navbar } from "./components/Navbar";
import { DashboardView } from "./pages/DashboardView";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { PublicPaymentPage } from "./pages/PublicPaymentPage";

export function App() {
  const [currentUser, setCurrentUser] = useState<UserSession | null>(() =>
    api.getCurrentUser(),
  );
  const [activeTab, setActiveTab] = useState<string>("dashboard");

  const handleLoginSuccess = (user: UserSession) => {
    setCurrentUser(user);
    setActiveTab("dashboard");
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
  };

  // If unauthenticated, present the official corporate login portal
  if (!currentUser) {
    return (
      <div
        style={{
          minHeight: "100vh",
          backgroundColor: "var(--paper)",
          color: "var(--ink)",
        }}>
        <ColdStartBanner />
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  // Authenticated enterprise portal
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "var(--paper)",
        color: "var(--ink)",
        display: "flex",
        flexDirection: "column",
      }}>
      {/* Cold-start detection banner */}
      <ColdStartBanner />

      {/* Official Enterprise Navigation Bar */}
      <Navbar
        currentUser={currentUser}
        activeTab={activeTab}
        onNavigate={setActiveTab}
        onLogout={handleLogout}
        onUserChange={setCurrentUser}
      />

      {/* Main Corporate Workspace */}
      <main style={{ flex: 1 }}>
        {activeTab === "dashboard" && (
          <DashboardView currentUser={currentUser} onNavigate={setActiveTab} />
        )}

        {activeTab === "public_invoice" && (
          <PublicPaymentPage onBackToApp={() => setActiveTab("dashboard")} />
        )}

        {activeTab === "architecture" && (
          <LandingPage
            onLoginPersona={setCurrentUser}
            onNavigate={setActiveTab}
          />
        )}
      </main>

      {/* Enterprise Footer */}
      <footer
        style={{
          borderTop: "1px solid var(--line)",
          backgroundColor: "var(--surface)",
          padding: "20px 24px",
          textAlign: "center",
          fontSize: "var(--t-small)",
          color: "var(--ink-3)",
          marginTop: "40px",
        }}>
        <div
          style={{
            maxWidth: "1440px",
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "12px",
          }}>
          <span>
            © 2026 <strong>PT Lumbung Pangan Nusantara</strong>. Hak Cipta
            Dilindungi Undang-Undang.
          </span>
          <span style={{ fontSize: "0.75rem", color: "var(--ink-3)" }}>
            Sistem Informasi Operasional Terpadu • Zero-Float Integer Currency •
            Append-Only Ledger
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
