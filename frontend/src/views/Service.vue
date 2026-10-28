<template>
  <div v-if="page" class="page">
    <h1>{{ page.title }}</h1>
    <div class="body">{{ page.body }}</div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { site } from '../site'

const router = useRouter()
const page = site.servicePage

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
.body {
  white-space: pre-line;
  line-height: 1.85;
  color: #303133;
  font-size: 16px;
}

@media (max-width: 768px) {
  .page {
    padding: 16px 0 32px;
  }
  h1 {
    font-size: 26px;
  }
}
</style>
