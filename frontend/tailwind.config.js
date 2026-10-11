/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        paper: "var(--paper)",
        surface: {
          DEFAULT: "var(--surface)",
          2: "var(--surface-2)",
          hover: "var(--surface-hover)",
        },
        line: {
          DEFAULT: "var(--line)",
          strong: "var(--line-strong)",
        },
        ink: {
          DEFAULT: "var(--ink)",
          2: "var(--ink-2)",
          3: "var(--ink-3)",
        },
        grain: {
          DEFAULT: "var(--grain)",
          hover: "var(--grain-hover)",
          wash: "var(--grain-wash)",
        },
        amber: {
          DEFAULT: "var(--amber)",
          wash: "var(--amber-wash)",
        },
        brick: {
          DEFAULT: "var(--brick)",
          wash: "var(--brick-wash)",
        },
        moss: {
          DEFAULT: "var(--moss)",
          wash: "var(--moss-wash)",
        },
        slate: {
          DEFAULT: "var(--slate)",
          wash: "var(--slate-wash)",
        },
      },
      fontFamily: {
        ui: "var(--font-ui)",
        num: "var(--font-num)",
        serif: "var(--font-serif)",
      },
      borderRadius: {
        DEFAULT: "var(--radius)",
        dialog: "var(--radius-dialog)",
        tag: "var(--radius-tag)",
      },
      boxShadow: {
        float: "var(--shadow-float)",
      },
      height: {
        row: "var(--row-h)",
        "row-dense": "var(--row-h-dense)",
      },
    },
  },
  plugins: [],
};
