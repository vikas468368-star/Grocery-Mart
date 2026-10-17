/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pos: {
          dark: '#0b0f19',
          card: '#1a233a',
          surface: '#131b2e',
          border: '#263353',
          emerald: '#10b981',
          blue: '#3b82f6',
          amber: '#f59e0b',
          rose: '#f43f5e',
          text: '#f8fafc',
          muted: '#94a3b8',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
