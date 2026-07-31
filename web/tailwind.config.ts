import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        mantis: {
          50: "#f0f7ff",
          100: "#e0effe",
          200: "#b9dffd",
          300: "#7cc4fc",
          400: "#36a6f8",
          500: "#0c8be9",
          600: "#006ec7",
          700: "#0058a1",
          800: "#044b85",
          900: "#0a3f6e",
          950: "#062849",
        },
        risk: {
          low: "#22c55e",
          medium: "#f59e0b",
          high: "#ef4444",
          critical: "#dc2626",
        },
        severity: {
          info: "#3b82f6",
          warning: "#f59e0b",
          critical: "#ef4444",
          emergency: "#dc2626",
        },
      },
    },
  },
  plugins: [],
};
export default config;
