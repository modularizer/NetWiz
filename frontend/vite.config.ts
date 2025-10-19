import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: process.env.BASE_URL || (process.env.NODE_ENV === 'production' ? '/NetWiz/' : '/'),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  define: {
    'import.meta.env.VITE_BASE_URL': JSON.stringify(process.env.BASE_URL || '/'),
    'import.meta.env.VITE_BACKEND_BASE_URL': JSON.stringify(process.env.BACKEND_BASE_URL || 'http://localhost:5000'),
    'import.meta.env.VITE_BACKEND_PORT': JSON.stringify(process.env.BACKEND_PORT || '5000'),
  },
})
