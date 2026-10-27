import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// 本机热更新开发：
//   前台 Vite  = 8001（浏览器访问这个端口）
//   后台 API   = 18001（由 Vite 把 /api 代理过去）
// Ubuntu 测试主机不要用这套：那边只用 start.sh，页面和接口都在 8001。
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
