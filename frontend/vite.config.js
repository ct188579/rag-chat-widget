import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import dts from 'vite-plugin-dts';
import { resolve } from 'path';
export default defineConfig({
    plugins: [
        react(),
        dts({
            include: ['src'],
            exclude: ['src/**/*.test.ts', 'src/**/*.stories.tsx', 'src/main.tsx', 'src/dev.tsx'],
            beforeWriteFile: (filePath, content) => {
                return {
                    filePath,
                    content: content.replace(/import\s+React[^;]*;/g, ''),
                };
            },
        }),
    ],
    publicDir: false,
    build: {
        lib: {
            entry: resolve(__dirname, 'src/index.ts'),
            name: 'AiChatWidget',
            formats: ['es', 'umd'],
            fileName: (format) => {
                if (format === 'umd')
                    return 'ai-chat-widget.umd.cjs';
                return 'ai-chat-widget.js';
            },
        },
        rollupOptions: {
            external: ['react', 'react-dom', 'react/jsx-runtime'],
            output: {
                globals: {
                    react: 'React',
                    'react-dom': 'ReactDOM',
                    'react/jsx-runtime': 'react/jsx-runtime',
                },
                assetFileNames: 'style.[ext]',
            },
        },
        outDir: 'dist',
        emptyOutDir: true,
        sourcemap: true,
        minify: 'esbuild',
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
});
