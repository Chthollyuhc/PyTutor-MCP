import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Mặc định: Vite :5173 → backend :8000. Khi QA trên DB cô lập có thể chạy một cặp riêng bằng
// PYTUTOR_VITE_PORT và PYTUTOR_API_TARGET (xem cấu hình "qa-*" trong .claude/launch.json).
const apiTarget = process.env.PYTUTOR_API_TARGET || 'http://127.0.0.1:8000'
const devPort = Number(process.env.PYTUTOR_VITE_PORT) || 5173

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: devPort,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      }
    }
  }
})
