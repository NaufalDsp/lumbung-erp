import React from "react";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
  showText?: boolean;
}

export const Logo: React.FC<LogoProps> = ({
  size = "md",
  showTagline = true,
  showText = true,
}) => {
  const iconSizes = {
    sm: { width: 24, height: 24 },
    md: { width: 32, height: 32 },
    lg: { width: 44, height: 44 },
  };

  const textSizes = {
    sm: { title: "0.95rem", badge: "0.65rem", tagline: "0.65rem" },
    md: { title: "1.15rem", badge: "0.75rem", tagline: "0.72rem" },
    lg: { title: "1.6rem", badge: "0.85rem", tagline: "0.8rem" },
  };

  const isDark =
    typeof document !== "undefined" &&
    document.documentElement.getAttribute("data-theme") === "dark";
  const primaryColor = isDark ? "#8FBF98" : "#2F4A3A";
  const textColor = isDark ? "#EDE9DC" : "#1D1C17";
  const subColor = isDark ? "#8A8675" : "#7A7667";
  const badgeBg = isDark ? "#223228" : "#E4ECE3";

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: size === "sm" ? "8px" : "12px",
        textDecoration: "none",
      }}>
      {/* SVG Icon Mark */}
      <svg
        viewBox="0 0 48 48"
        width={iconSizes[size].width}
        height={iconSizes[size].height}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ flexShrink: 0 }}>
        <path
          d="M6 18L24 6L42 18L38 22L24 12L10 22L6 18Z"
          fill={primaryColor}
        />
        <rect
          x="12"
          y="22"
          width="6"
          height="20"
          rx="1.5"
          fill={primaryColor}
        />
        <rect
          x="30"
          y="22"
          width="6"
          height="20"
          rx="1.5"
          fill={primaryColor}
        />
        <rect
          x="21"
          y="24"
          width="6"
          height="18"
          rx="1.5"
          fill={primaryColor}
          opacity={0.85}
        />
        <circle cx="24" cy="18" r="3.5" fill="#9A5B13" />
        <path
          d="M24 15V21M21 18H27"
          stroke="#FFFFFF"
          strokeWidth="1.2"
          strokeLinecap="round"
        />
        <rect x="8" y="41" width="32" height="3" rx="1.5" fill={primaryColor} />
      </svg>

      {/* Typography */}
      {showText && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              lineHeight: 1.1,
            }}>
            <span
              style={{
                fontFamily: "var(--font-ui)",
                fontWeight: 700,
                fontSize: textSizes[size].title,
                color: textColor,
                letterSpacing: "-0.02em",
              }}>
              LUMBUNG
            </span>
            <span
              style={{
                fontFamily: "var(--font-num)",
                fontWeight: 600,
                fontSize: textSizes[size].badge,
                backgroundColor: badgeBg,
                color: primaryColor,
                padding: "1px 6px",
                borderRadius: "var(--radius-tag)",
                border: `1px solid ${primaryColor}22`,
              }}>
              ERP
            </span>
          </div>
          {showTagline && (
            <span
              style={{
                fontFamily: "var(--font-ui)",
                fontSize: textSizes[size].tagline,
                color: subColor,
                fontWeight: 500,
                letterSpacing: "0.04em",
                marginTop: "2px",
              }}>
              SISTEM MANAJEMEN DISTRIBUSI PANGAN
            </span>
          )}
        </div>
      )}
    </div>
  );
};
