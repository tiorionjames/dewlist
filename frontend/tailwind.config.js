// frontend/tailwind.config.js
import { defineConfig } from 'tailwindcss'

export default defineConfig({
  // ✂ darkMode: 'class',   ← remove this line
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
    './index.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1FB6FF',
          // dark: '#0D8FDB',   ← drop this too
        },
        accent: {
          DEFAULT: '#FF49DB',
          // dark: '#DB2FA8',
        },
        neutral: {
          DEFAULT: '#E5E7EB',
          // dark: '#2A2A2A',
        },
        surface: '#333333',
      },
    },
  },
  plugins: [],
})
