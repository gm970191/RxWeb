<template>
  <div v-if="page" class="page-shell">
    <PageBanner :title="page.title" :image="page.banner" />
    <div class="page-sheet body">{{ page.body }}</div>
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
.body {
  white-space: pre-line;
  line-height: 1.85;
  color: #303133;
  font-size: 16px;
}
</style>
