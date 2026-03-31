import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const proxyTarget =
  process.env.VITE_PROXY_TARGET || process.env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
})
