import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'static',
    assetsDir: '',
    rollupOptions: {
      input: {
        main: './src/blog_chat/main.ts',
      },
      output: {
        entryFileNames: 'main.js',
        assetFileNames: 'main[extname]',
      },
    },
  },
})
