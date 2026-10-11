import React from "react";

export function App() {
  return (
    <div style={{ padding: "24px", maxWidth: "1280px", margin: "0 auto" }}>
      <header
        style={{
          borderBottom: "1px solid var(--line)",
          paddingBottom: "16px",
          marginBottom: "24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
        <div>
          <h1 style={{ fontSize: "var(--t-page)", fontWeight: 600 }}>
            Lumbung ERP
          </h1>
          <p style={{ color: "var(--ink-2)", fontSize: "var(--t-small)" }}>
            Mini ERP alur pesanan sampai faktur
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button className="btn-secondary">Dokumentasi</button>
          <button className="btn-primary">Masuk Demo</button>
        </div>
      </header>

      <main>
        <section
          style={{
            backgroundColor: "var(--surface)",
            border: "1px solid var(--line)",
            borderRadius: "var(--radius)",
            padding: "24px",
          }}>
          <h2 style={{ fontSize: "var(--t-doc)", marginBottom: "8px" }}>
            Status Inisialisasi Sistem
          </h2>
          <p style={{ color: "var(--ink-2)", marginBottom: "16px" }}>
            Fondasi arsitektur bersih (Clean Architecture & Design Tokens) telah
            disiapkan.
          </p>
          <div style={{ display: "flex", gap: "16px" }}>
            <span style={{ color: "var(--moss)" }}>● Frontend siap</span>
            <span style={{ color: "var(--moss)" }}>● Token CSS aktif</span>
            <span style={{ color: "var(--slate)" }}>
              ○ Backend v1 /api/v1/health
            </span>
          </div>
        </section>
      </main>
    </div>
  );
}
