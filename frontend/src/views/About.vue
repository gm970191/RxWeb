<template>
  <div v-if="page" class="page">
    <h1>{{ page.title }}</h1>
    <p v-for="(paragraph, index) in page.paragraphs" :key="index">{{ paragraph }}</p>
    <div v-if="page.advantages?.length" class="advantages">
      <h2>服务优势</h2>
      <div class="advantage-grid">
        <article v-for="item in page.advantages" :key="item.title">
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </div>
    <div v-if="page.images?.length" class="photos">
      <img v-for="image in page.images" :key="image" :src="image" alt="" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { site } from '../site'

const router = useRouter()
const page = site.aboutPage

onMounted(() => {
  if (!page) router.replace('/')
})
</script>

<style scoped>
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 0 48px;
}
h1 {
  margin: 0 0 20px;
  font-size: 32px;
  color: #0b3d73;
}
p {
  margin: 0 0 16px;
  line-height: 1.85;
  color: #303133;
  font-size: 16px;
}
h2 {
  margin: 28px 0 16px;
  font-size: 22px;
  color: #0b3d73;
}
.advantage-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
article {
  padding: 16px 18px;
  border: 1px solid #e4e7ed;
  border-top: 3px solid #f0b429;
  border-radius: 8px;
  background: #fff;
}
h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #0b3d73;
}
article p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}
.photos {
  display: grid;
  gap: 16px;
  margin-top: 28px;
}
.photos img {
  width: 100%;
  max-height: 280px;
  object-fit: cover;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .page {
    padding: 16px 0 32px;
  }
  h1 {
    font-size: 26px;
  }
  .advantage-grid {
    grid-template-columns: 1fr;
  }
}
</style>
