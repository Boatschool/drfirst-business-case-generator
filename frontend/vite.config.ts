/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh for better dev experience
      fastRefresh: true,
      // Use automatic JSX runtime for better performance
      jsxRuntime: 'automatic',
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/services': resolve(__dirname, 'src/services'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/utils': resolve(__dirname, 'src/utils'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 4000,
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
      'Cross-Origin-Embedder-Policy': 'unsafe-none',
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    // Optimize build performance
    target: 'es2020',
    cssCodeSplit: true,
    sourcemap: false, // Disable in production for better performance
    minify: 'esbuild', // Use esbuild for faster minification
    assetsInlineLimit: 4096, // Inline small assets as base64
    reportCompressedSize: false, // Disable gzip size reporting for faster builds
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Core React libraries
          'react-vendor': ['react', 'react-dom'],
          // Material-UI components (split into smaller chunks)
          'mui-core': ['@mui/material/Button', '@mui/material/TextField', '@mui/material/Typography'],
          'mui-layout': ['@mui/material/Container', '@mui/material/Box', '@mui/material/Grid'],
          'mui-icons': ['@mui/icons-material'],
          'mui-system': ['@emotion/react', '@emotion/styled'],
          // Router and navigation
          'router-vendor': ['react-router-dom'],
          // HTTP and data fetching
          'http-vendor': ['axios', '@tanstack/react-query'],
          // Firebase (split into smaller chunks)
          'firebase-app': ['firebase/app'],
          'firebase-auth': ['firebase/auth'],
          'firebase-firestore': ['firebase/firestore'],
          // Markdown rendering
          'markdown-vendor': ['react-markdown'],
        },
        // Optimize chunk names for better caching
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `assets/[name]-[hash].js`;
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return `assets/images/[name]-[hash][extname]`;
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return `assets/fonts/[name]-[hash][extname]`;
          }
          if (/\.(css)$/i.test(assetInfo.name)) {
            return `assets/css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
      // Performance optimizations
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
      },
    },
    // Increase chunk size limit to reduce the number of chunks
    chunkSizeWarningLimit: 1000,
  },
  // Performance optimizations
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@mui/material',
      '@mui/icons-material',
      'react-router-dom',
      'axios',
      '@tanstack/react-query',
      'firebase/app',
      'firebase/auth',
      'firebase/firestore',
      'react-markdown'
    ],
    // Force bundling of these dependencies
    force: true,
  },
  // Experimental features for better performance
  experimental: {
    renderBuiltUrl(filename, { hostType }) {
      if (hostType === 'css') {
        // Use relative URLs in CSS for better CDN compatibility
        return { relative: true };
      }
      return { runtime: `window.__assetsPath(${JSON.stringify(filename)})` };
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    css: true,
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/setupTests.ts'],
    },
  },
});
