import { defineConfig } from 'vite'
import { viteStaticCopy } from 'vite-plugin-static-copy'

export default defineConfig({
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'src/assets/favicon/*',
          dest: '',
        },
        {
          src: 'src/assets/posts/*',
          dest: 'posts',
        },
      ],
    }),
  ],
  build: {
    outDir: 'static',
    assetsDir: '',
    rollupOptions: {
      input: {
        main: './src/blog_chat/core/client/main.ts',
        chat: './src/blog_chat/features/chat/client/main.ts',
        posts: './src/blog_chat/features/posts/client/main.ts',
        "audio-puzzle": './src/blog_chat/features/posts/client/audio-puzzle.ts',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
})
