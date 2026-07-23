import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// In Docker Compose, VITE_BACKEND_URL is set to http://backend:8000 (the
// service name, resolved over the Compose network). Outside Docker it falls
// back to 127.0.0.1 for plain "npm run dev" usage.
const backendTarget = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    // Vite's dev server rejects requests whose Host header isn't
    // localhost/127.0.0.1 or explicitly allow-listed, as a security
    // measure against DNS-rebinding attacks. When this container is
    // accessed through a remote proxy (e.g. Killercoda, ngrok, Codespaces),
    // the Host header is the proxy's public domain, so Vite silently drops
    // the request — the proxy in front then reports that as a 502. Setting
    // allowedHosts to true disables this check. Fine for local/sandboxed
    // dev environments; do not do this for a production-exposed server.
    allowedHosts: true,
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/media': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
})
