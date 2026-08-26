import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      // dev 中の /api/* を backend へ中継する。これがあるので CORS 設定は不要。
      // localhost ではなく 127.0.0.1 と書くこと。Node は localhost を ::1 に先に解決するため、
      // uvicorn が IPv4 のみで待ち受けていると接続に失敗する。
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
