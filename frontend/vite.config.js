import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // ビルド設定: Flask の static/js/shift-editor/ に出力
  build: {
    outDir: '../static/js/shift-editor',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  
  // 開発時: Flask API へプロキシ
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5050',
        changeOrigin: true
      },
      '/admin': {
        target: 'http://localhost:5050',
        changeOrigin: true
      }
    }
  }
})
