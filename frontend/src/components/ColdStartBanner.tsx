import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export const ColdStartBanner: React.FC = () => {
  const [isCold, setIsCold] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    const unsubscribe = api.subscribeColdStart((val) => {
      setIsCold(val);
    });

    // Check health on initial load
    api.checkHealth();

    return () => unsubscribe();
  }, []);

  const handleRetry = async () => {
    setIsChecking(true);
    await api.checkHealth();
    setIsChecking(false);
  };

  if (!isCold) return null;

  return (
    <div
      style={{
        backgroundColor: "var(--amber-wash)",
        borderBottom: "1px solid var(--amber)",
        color: "var(--ink)",
        padding: "10px 24px",
        fontSize: "var(--t-small)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span
          style={{
            display: "inline-block",
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            backgroundColor: "var(--amber)",
            animation: "pulse 1.5s infinite",
          }}
        />
        <span>
          <strong>Server sedang bersiap (Cold Start ~15–30 detik).</strong>{" "}
          Layanan gratis hosting backend sedang bangun dari mode tidur. Mohon
          tunggu sejenak.
        </span>
      </div>
      <button
        onClick={handleRetry}
        disabled={isChecking}
        className="btn-secondary"
        style={{ padding: "4px 12px", fontSize: "0.75rem" }}>
        {isChecking ? "Memeriksa..." : "Cek Ulang Koneksi"}
      </button>
    </div>
  );
};
