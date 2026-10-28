<template>
  <div v-if="page" class="page">
    <PageBanner :title="page.title" :image="page.banner" />
    <div class="sheet">
      <p v-for="(paragraph, index) in page.paragraphs" :key="index">{{ paragraph }}</p>
    </div>
    <div v-if="page.advantages?.length" class="advantages">
      <h2>服务优势</h2>
      <div class="advantage-grid">
        <article v-for="item in page.advantages" :key="item.title">
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageBanner from '../components/PageBanner.vue'
import { site } from '../site'

const router = useRouter()
const page = site.aboutPage

onMounted(() => {
  if (!page) router.replace('/')
})
</script>

<style scoped>
.page {
  max-width: 960px;
  margin: 0 auto;
  padding: 8px 0 48px;
}
.sheet {
  padding: 28px 32px 12px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(11, 61, 115, 0.06);
}
p {
  margin: 0 0 16px;
  line-height: 1.85;
  color: #303133;
  font-size: 16px;
}
h2 {
  margin: 8px 0 16px;
  font-size: 22px;
  color: #0b3d73;
}
.advantages {
  margin-top: 12px;
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

@media (max-width: 768px) {
  .page {
    padding: 0 0 32px;
  }
  .sheet {
    padding: 18px 16px 4px;
  }
  .advantage-grid {
    grid-template-columns: 1fr;
  }
}
</style>
