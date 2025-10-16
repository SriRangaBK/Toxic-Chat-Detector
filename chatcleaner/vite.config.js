import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  // *** CRITICAL FIX: Set base URL to match Django's STATIC_URL ***
  base: '/static/', 
});