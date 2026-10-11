import React, { useState } from "react";
import { formatRupiah } from "../lib/formatters";

interface PublicPaymentPageProps {
  onBackToApp: () => void;
}

export const PublicPaymentPage: React.FC<PublicPaymentPageProps> = ({
  onBackToApp,
}) => {
  const [isPaying, setIsPaying] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  // Demo invoice data simulating public portal view
  const invoice = {
    number: "INV-2025-000001",
    customer_name: "Toko Sembako Berkah Jaya",
    company_name: "PT Lumbung Pangan Nusantara",
    issued_at: "11 Okt 2026",
    due_at: "25 Okt 2026",
    status: paymentSuccess ? "LUNAS" : "TERBIT",
    lines: [
      {
        product_name: "Beras Pandan Wangi 5kg",
        qty: 20,
        unit_price: 75000,
        subtotal: 1500000,
      },
      {
        product_name: "Minyak Goreng Sawit 2L",
        qty: 10,
        unit_price: 34000,
        subtotal: 340000,
      },
      {
        product_name: "Gula Pasir Kristal 1kg",
        qty: 50,
        unit_price: 16500,
        subtotal: 825000,
      },
    ],
    subtotal: 2665000,
    tax: 293150, // 11% PPN integer half-up: (2665000 * 1100 + 5000) // 10000
    total: 2958150,
  };

  const handlePay = () => {
    setIsPaying(true);
    setTimeout(() => {
      setIsPaying(false);
      setPaymentSuccess(true);
      alert(
        "Simulasi pembayaran Midtrans Snap berhasil diselesaikan (Status: LUNAS)!",
      );
    }, 1200);
  };

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", padding: "0 24px" }}>
      <button
        onClick={onBackToApp}
        className="btn-secondary"
        style={{
          marginBottom: "20px",
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
        }}>
        ← Kembali ke Aplikasi ERP
      </button>

      <div
        style={{
          backgroundColor: "var(--surface)",
          border: "1px solid var(--line)",
          borderRadius: "var(--radius)",
          padding: "36px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
        }}>
        {/* Invoice Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            borderBottom: "1px solid var(--line)",
            paddingBottom: "24px",
            marginBottom: "24px",
          }}>
          <div>
            <span
              style={{
                fontSize: "0.8rem",
                color: "var(--grain)",
                fontWeight: 700,
                textTransform: "uppercase",
              }}>
              Faktur Tagihan Resmi
            </span>
            <h1
              style={{
                fontSize: "1.75rem",
                fontWeight: 700,
                color: "var(--ink)",
                margin: "4px 0",
              }}>
              {invoice.number}
            </h1>
            <p style={{ color: "var(--ink-2)", fontSize: "var(--t-small)" }}>
              Diterbitkan oleh: <strong>{invoice.company_name}</strong>
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <span
              style={{
                display: "inline-block",
                padding: "6px 12px",
                borderRadius: "var(--radius-tag)",
                fontWeight: 700,
                fontSize: "0.85rem",
                backgroundColor:
                  invoice.status === "LUNAS"
                    ? "var(--moss-wash)"
                    : "var(--amber-wash)",
                color:
                  invoice.status === "LUNAS" ? "var(--moss)" : "var(--amber)",
              }}>
              ● {invoice.status}
            </span>
          </div>
        </div>

        {/* Customer & Due Date Info */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "20px",
            marginBottom: "32px",
            fontSize: "var(--t-small)",
          }}>
          <div>
            <div style={{ color: "var(--ink-3)", marginBottom: "4px" }}>
              Ditagihkan Kepada:
            </div>
            <div
              style={{
                fontWeight: 600,
                color: "var(--ink)",
                fontSize: "1rem",
              }}>
              {invoice.customer_name}
            </div>
            <div style={{ color: "var(--ink-2)" }}>
              Komp. Ruko Pasar Induk No. 12
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "var(--ink-3)", marginBottom: "4px" }}>
              Batas Pembayaran:
            </div>
            <div
              style={{
                fontWeight: 600,
                color: "var(--brick)",
                fontSize: "1rem",
              }}>
              {invoice.due_at}
            </div>
            <div style={{ color: "var(--ink-2)" }}>
              Tanggal Terbit: {invoice.issued_at}
            </div>
          </div>
        </div>

        {/* Itemized Table */}
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginBottom: "28px",
          }}>
          <thead>
            <tr
              style={{
                borderBottom: "2px solid var(--line)",
                textAlign: "left",
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
              }}>
              <th style={{ padding: "8px 0" }}>Barang</th>
              <th style={{ padding: "8px 0", textAlign: "right" }}>Jumlah</th>
              <th style={{ padding: "8px 0", textAlign: "right" }}>
                Harga Satuan
              </th>
              <th style={{ padding: "8px 0", textAlign: "right" }}>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {invoice.lines.map((item, idx) => (
              <tr
                key={idx}
                style={{
                  borderBottom: "1px solid var(--line)",
                  fontSize: "var(--t-body)",
                }}>
                <td style={{ padding: "12px 0", color: "var(--ink)" }}>
                  {item.product_name}
                </td>
                <td
                  style={{ padding: "12px 0", textAlign: "right" }}
                  className="num">
                  {item.qty} unit
                </td>
                <td
                  style={{ padding: "12px 0", textAlign: "right" }}
                  className="num">
                  {formatRupiah(item.unit_price)}
                </td>
                <td
                  style={{
                    padding: "12px 0",
                    textAlign: "right",
                    fontWeight: 600,
                  }}
                  className="num">
                  {formatRupiah(item.subtotal)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Calculation Summary */}
        <div
          style={{
            maxWidth: "320px",
            marginLeft: "auto",
            marginBottom: "32px",
            fontSize: "var(--t-body)",
          }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "8px",
            }}>
            <span style={{ color: "var(--ink-2)" }}>Subtotal</span>
            <span className="num" style={{ fontWeight: 500 }}>
              {formatRupiah(invoice.subtotal)}
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "8px",
            }}>
            <span style={{ color: "var(--ink-2)" }}>
              PPN (11% Integer Basis Points)
            </span>
            <span className="num" style={{ fontWeight: 500 }}>
              {formatRupiah(invoice.tax)}
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              borderTop: "2px solid var(--line)",
              paddingTop: "12px",
              fontSize: "1.15rem",
              fontWeight: 700,
              color: "var(--ink)",
            }}>
            <span>Total Tagihan</span>
            <span className="num" style={{ color: "var(--grain)" }}>
              {formatRupiah(invoice.total)}
            </span>
          </div>
        </div>

        {/* Checkout Button */}
        {!paymentSuccess ? (
          <div
            style={{
              textAlign: "center",
              borderTop: "1px solid var(--line)",
              paddingTop: "24px",
            }}>
            <p
              style={{
                fontSize: "var(--t-small)",
                color: "var(--ink-3)",
                marginBottom: "16px",
              }}>
              Pembayaran aman diproses langsung via payment gateway Midtrans
              (QRIS, BCA Virtual Account, Mandiri, GoPay).
            </p>
            <button
              onClick={handlePay}
              disabled={isPaying}
              className="btn-primary"
              style={{
                padding: "12px 32px",
                fontSize: "1rem",
                fontWeight: 600,
              }}>
              {isPaying
                ? "Menghubungkan ke Snap..."
                : `Bayar Sekarang (${formatRupiah(invoice.total)})`}
            </button>
          </div>
        ) : (
          <div
            style={{
              textAlign: "center",
              backgroundColor: "var(--moss-wash)",
              padding: "16px",
              borderRadius: "var(--radius)",
            }}>
            <span style={{ color: "var(--moss)", fontWeight: 600 }}>
              ✓ Terima kasih! Tagihan telah lunas dibayar.
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
