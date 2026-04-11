import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,

        // ── Vite Dev Proxy ──────────────────────────────────────────────────
        // Routes /api/* to the FastAPI backend on port 8000.
        // This runs server-side so the browser never makes a cross-origin request
        // — eliminating all CORS issues during development, including the
        // Authorization header stripping caused by allow_credentials=False.
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
                rewrite: (path) => path, // keep /api prefix intact
            }
        }
    }
})
