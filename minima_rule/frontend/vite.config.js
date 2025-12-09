import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true
  },
  resolve: {
    alias: {
      'node-fetch': 'isomorphic-fetch'
    },
    fallback: {
      "fs": false,
      "path": false,
      "os": false,
      "tls": false,
      "net": false,
      "crypto": false,
      "stream": false,
      "buffer": false
    }
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: 'globalThis'
      }
    }
  }
})