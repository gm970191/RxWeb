<template>
  <div v-if="page" class="page">
    <PageBanner :title="page.title" :image="page.banner" />
    <div class="body">{{ page.body }}</div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageBanner from '../components/PageBanner.vue'
import { site } from '../site'

const router = useRouter()
const page = site.servicePage

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
.body {
  padding: 28px 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(11, 61, 115, 0.06);
  white-space: pre-line;
  line-height: 1.85;
  color: #303133;
  font-size: 16px;
}

@media (max-width: 768px) {
  .page {
    padding: 0 0 32px;
  }
  .body {
    padding: 18px 16px;
  }
}
</style>
