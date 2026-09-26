import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Suisse Intl Trial"', '"Suisse Intl"', "Satoshi", "-apple-system", "system-ui", "sans-serif"],
        mono: ["Menlo", '"JetBrains Mono"', "monospace"],
      },
      colors: {
        canvas: "#0f0e0d",
        surface: "#1a1815",
        "surface-2": "#221f1c",
        "surface-3": "#2a2622",
        border: "#2e2a26",
        "border-strong": "#3d3830",
        "text-primary": "#f0ece8",
        "text-secondary": "#9a9088",
        "text-muted": "#6b6358",
        primary: "#F94612",
        "primary-hover": "#D93A0B",
        "primary-press": "#B32E08",
        "primary-glow": "rgba(249,70,18,0.25)",
        success: "#2ab870",
        "success-bg": "rgba(42,184,112,0.12)",
        error: "#f04040",
        "error-bg": "rgba(240,64,64,0.12)",
        warning: "#e89c2a",
        "warning-bg": "rgba(232,156,42,0.12)",
      },
      borderRadius: {
        xs: "3px",
        sm: "6px",
        md: "8px",
        lg: "10px",
        xl: "16px",
      },
      transitionTimingFunction: {
        spring: "cubic-bezier(.34, 1.36, .64, 1)",
        "ease-out": "cubic-bezier(.23, 1, .32, 1)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 180ms ease-out forwards",
      },
    },
  },
  plugins: [],
};

export default config;
