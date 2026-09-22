import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: true,
    // Bind mount do Windows via Docker Desktop não propaga eventos de
    // arquivo de forma confiável para o container — sem polling, o Vite
    // não recarrega mudanças feitas no host.
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
})
