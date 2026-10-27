<style>
@import "./assets/main.css";
</style>
<template>
  <div id="app">
    <nav>
      <router-link to="/">主页</router-link>
      <router-link to="/products">产品介绍</router-link>
      <router-link to="/news">新闻动态</router-link>
      <router-link to="/resources">资源下载</router-link>
      <router-link to="/contact">联系我们</router-link>
    </nav>
    <router-view></router-view>
  </div>
</template>
<script>
export default {
  name: 'App'
}
</script>
<style scoped>
/* 可以添加额外的局部样式 */
</style>