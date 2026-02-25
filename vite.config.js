import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'static',
    assetsDir: '',
    rollupOptions: {
      input: {
        main: './src/blog_chat/core/client/main.ts',
        chat: './src/blog_chat/features/chat/client/main.ts',
        posts: './src/blog_chat/features/posts/client/main.ts',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
})
