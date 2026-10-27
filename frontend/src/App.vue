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

.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 768px) {
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