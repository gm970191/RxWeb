<template>
  <div>
    <h1>联系我们</h1>
    <h2>公司详情</h2>
    <p>地址：示例地址 123 号</p>
    <p>电话：123-456-7890</p>
    <p>邮箱：contact@company.com</p>
    <div id="map">
      <!-- 这里可以嵌入地图 API，例如 Google Maps 或百度地图 -->
      <iframe
        src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d12079.096767630973!2d-74.0060!3d40.7128!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQzLjkiTiA3NMKwMDAmMzIuOCJX!5e0!3m2!1sen!2sus!4v1629838433107!5m2!1sen!2sus"
        width="600"
        height="450"
        style="border:0;"
        allowfullscreen=""
        loading="lazy"
      ></iframe>
    </div>
    <h2>总裁致辞</h2>
    <p>我们致力于为客户提供最优质的产品和服务，感谢大家一直以来的支持。</p>
    <h2>招聘信息</h2>
    <ul>
      <li>职位 1：前端开发工程师</li>
      <li>职位 2：后端开发工程师</li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'Contact'
  }
</script>

<style scoped>
  #map {
    margin-top: 20px;
  }
</style>