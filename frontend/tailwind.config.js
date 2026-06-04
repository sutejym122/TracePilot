/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0a0c10",
        surface: {
          DEFAULT: "#11141b",
          raised: "#161a23",
          hover: "#1c212c",
        },
        border: {
          DEFAULT: "#222834",
          strong: "#2e3644",
        },
        content: {
          DEFAULT: "#e6e9ef",
          muted: "#8b93a3",
          faint: "#5b6373",
        },
        signal: {
          DEFAULT: "#2dd4bf",
          dim: "#15514a",
        },
        status: {
          healthy: "#34d399",
          degraded: "#fbbf24",
          down: "#f87171",
          unknown: "#6b7280",
          ready: "#34d399",
          risky: "#fbbf24",
          blocked: "#f87171",
          critical: "#f87171",
          high: "#fb923c",
          medium: "#fbbf24",
          low: "#60a5fa",
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.02) inset",
      },
    },
  },
  plugins: [],
};
