import { defineConfig } from 'vite'
import { viteStaticCopy } from 'vite-plugin-static-copy'

function copyPuzzleAlias() {
  return {
    name: 'copy-puzzle-alias',
    async writeBundle() {
      const { copyFile } = await import('fs/promises');
      try { await copyFile('static/puzzle.js', 'static/audio-puzzle.js'); } catch {}
    }
  };
}

export default defineConfig({
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'src/assets/favicon/*',
          dest: '',
        },
      ],
    }),
    copyPuzzleAlias(),
  ],
  build: {
    outDir: 'static',
    assetsDir: '',
    rollupOptions: {
      input: {
        main: './src/blog_chat/core/client/main.ts',
        chat: './src/blog_chat/features/chat/client/main.ts',
        posts: './src/blog_chat/features/posts/client/main.ts',
        puzzle: './src/blog_chat/features/posts/client/puzzle.ts',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
})
