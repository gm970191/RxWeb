<template>
  <el-container class="app-container">
    <TheHeader />
    <el-main>
      <router-view />
    </el-main>
    <TheFooter />
  </el-container>
</template>

<script setup>
import TheHeader from './components/TheHeader.vue';
import TheFooter from './components/TheFooter.vue';
</script>

<style>
/* Global styles */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  max-width: 100%;
  overflow-x: hidden;
  -webkit-text-size-adjust: 100%;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background: #f4f7fb;
}

img,
video,
canvas,
svg {
  max-width: 100%;
}

:root {
  --rx-page-width: 1200px;
  --rx-banner-height: 220px;
  --rx-banner-offset: 8px;
  --rx-page-bottom: 32px;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main {
  flex: 1;
  padding: 20px;
  min-width: 0;
}

.page-shell {
  max-width: var(--rx-page-width);
  margin: 0 auto;
  padding: var(--rx-banner-offset) 0 var(--rx-page-bottom);
}

.page-sheet {
  padding: 28px 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(11, 61, 115, 0.06);
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 768px) {
  :root {
    --rx-banner-height: 160px;
    --rx-banner-offset: 0px;
    --rx-page-bottom: 16px;
  }

  .page-sheet {
    padding: 18px 16px;
  }

  .el-main {
    padding: 12px;
  }

  .el-pagination {
    flex-wrap: wrap;
    justify-content: center;
  }

  .el-dialog {
    width: 92% !important;
    margin: 8vh auto !important;
  }

  .el-message-box {
    width: 90% !important;
    max-width: 420px;
  }
}
</style> 