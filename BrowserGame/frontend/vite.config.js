// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://10.0.0.80:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://10.0.0.80:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
});