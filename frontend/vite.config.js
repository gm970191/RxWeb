import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import fs from 'fs';
import path from 'path';

function resolveSite(command) {
  const fromEnv = (process.env.VITE_SITE_ID || '').trim();
  const siteId = fromEnv || (command === 'serve' ? 'ruixue' : '');
  if (!siteId) {
    throw new Error('构建前端必须设置 VITE_SITE_ID，一次只能构建一家公司');
  }
  if (!/^[A-Za-z0-9][A-Za-z0-9_-]*$/.test(siteId)) {
    throw new Error(`站点名不合法：${siteId}`);
  }
  const profile = path.resolve(__dirname, '../deploy/sites', siteId, 'profile.js');
  if (!fs.existsSync(profile)) {
    throw new Error(`找不到站点页面配置：${profile}`);
  }
  const text = fs.readFileSync(profile, 'utf8');
  const marked = text.match(/^\s*\/\/\s*site:\s*([A-Za-z0-9_-]+)/m);
  if (!marked || marked[1] !== siteId) {
    throw new Error(`页面配置不属于站点 ${siteId}`);
  }
  const name = text.match(/fullName:\s*'([^']+)'/);
  return {
    siteId,
    profile,
    siteName: (process.env.VITE_SITE_NAME || (name && name[1]) || siteId).trim(),
  };
}

// 仅 Windows 本机热更新使用。浏览器打开 8001。
// 发布时由 VITE_SITE_ID 指定站点，打包结果只包含这一家的页面配置。
export default defineConfig(({ command }) => {
  const site = resolveSite(command);
  return {
    plugins: [
      vue(),
      {
        name: 'site-title',
        transformIndexHtml(html) {
          return html.replaceAll('__SITE_TITLE__', site.siteName);
        },
      },
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'site-profile': site.profile,
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
  };
});
