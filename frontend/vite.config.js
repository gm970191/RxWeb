import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// 仅 Windows 本机热更新使用。浏览器打开 8001。
// 瑞学调试机不用这份代理，页面和接口都在 8001。
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 8001,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:18001',
        changeOrigin: true,
      },
    },
    historyApiFallback: true,
  },
});
