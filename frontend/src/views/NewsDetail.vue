<template>
  <div class="news-detail-container">
    <nav class="crumb" aria-label="当前位置">
      <router-link to="/news">新闻动态</router-link>
      <span class="sep" aria-hidden="true">/</span>
      <span aria-current="page">详情</span>
    </nav>
    <PageBanner title="新闻详情" :as-heading="false" />
    <el-card v-if="news">
      <h1 class="news-title">{{ news.title }}</h1>
      <div class="news-meta">
        <span>发布日期：{{ news.date }}</span>
        <span>来源：{{ news.source }}</span>
      </div>
      <div class="news-summary">{{ news.summary }}</div>
      <div class="news-content">{{ news.content }}</div>
    </el-card>
    <el-empty v-else description="未找到该新闻" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageBanner from '../components/PageBanner.vue'

const route = useRoute()
const news = ref(null)

onMounted(async () => {
  const id = route.params.id
  try {
    const resp = await fetch(`/api/news/${id}`)
    if (resp.ok) {
      const data = await resp.json()
      news.value = data.data
    } else {
      news.value = null
    }
  } catch (e) {
    news.value = null
  }
})
</script>

<style scoped>
.news-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px 0 32px;
}
.crumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  font-size: 15px;
  color: #909399;
}
.crumb a {
  color: #0b3d73;
  text-decoration: none;
}
.crumb a:hover {
  color: #1d6fb8;
}
.sep {
  color: #c0c4cc;
}
.news-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 16px;
}
.news-meta {
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}
.news-meta span {
  margin-right: 24px;
}
.news-summary {
  font-size: 16px;
  color: #606266;
  margin-bottom: 24px;
}
.news-content {
  font-size: 16px;
  color: #303133;
  line-height: 1.8;
  white-space: pre-line;
}

@media (max-width: 768px) {
  .news-detail-container {
    margin: 8px auto;
    padding: 0;
  }

  .news-title {
    font-size: 22px;
    line-height: 1.4;
    word-break: break-word;
  }

  .news-meta {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .news-meta span {
    margin-right: 0;
  }
}
</style> 