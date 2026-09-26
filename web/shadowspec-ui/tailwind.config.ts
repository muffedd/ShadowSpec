import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Geist", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ['"Geist Mono"', "Menlo", '"JetBrains Mono"', "monospace"],
      },
      colors: {
        canvas: "#f5f5f5",
        surface: "#ffffff",
        "surface-2": "#fafafa",
        "surface-3": "#f5f5f5",
        border: "#e5e5e5",
        "border-strong": "#d4d4d4",
        "text-primary": "#0a0a0a",
        "text-secondary": "#737373",
        "text-muted": "#a3a3a3",
        primary: "#171717",
        "primary-hover": "#0a0a0a",
        "primary-press": "#000000",
        success: "#171717",
        "success-bg": "#f5f5f5",
        error: "#e7000b",
        "error-bg": "#fdecec",
        warning: "#737373",
        "warning-bg": "#f5f5f5",
      },
      borderRadius: {
        xs: "6px",
        sm: "6px",
        md: "10px",
        lg: "18px",
        xl: "24px",
      },
      boxShadow: {
        card: "0 0 0 1px rgba(23,23,23,0.05), 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)",
      },
      transitionTimingFunction: {
        spring: "cubic-bezier(.34, 1.36, .64, 1)",
        "ease-out": "cubic-bezier(.23, 1, .32, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
