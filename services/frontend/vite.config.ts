import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['hypothesis-factory.geekiot.tech'],
  },
  preview: {
    allowedHosts: ['hypothesis-factory.geekiot.tech'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
