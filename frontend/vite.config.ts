import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // One origin during dev: no CORS, cookies just work (DESIGN.md §6.3 parity).
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
