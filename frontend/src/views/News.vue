<template>
  <div class="news-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>新闻动态</span>
          <div v-if="sourceOptions.length" class="source-bar">
            <button
              v-for="item in sourceOptions"
              :key="item"
              type="button"
              :class="{ active: selectedSource === item.value }"
              @click="selectSource(item.value)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </template>
      <div v-if="loading" style="text-align:center;padding:32px;">加载中...</div>
      <div v-else>
        <div v-for="item in newsList" :key="item.id" class="news-item">
          <div class="news-title">
            <a :href="`/news/${item.id}`" @click.prevent="goToDetail(item.id)">{{ item.title }}</a>
          </div>
          <div class="news-meta">
            <span>发布日期: {{ item.date }}</span>
            <span>来源: {{ item.source }}</span>
          </div>
          <p class="news-summary">{{ item.summary }}</p>
        </div>
      </div>
    </el-card>

    <div class="pagination-bar">
      <el-pagination
        background
        :small="true"
        layout="prev, pager, next"
        :pager-count="5"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchNews } from '../services/newsService'
import { site } from '../site'

const newsList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(5)
const loading = ref(false)
const selectedSource = ref(site.defaultNewsSource || '')
const router = useRouter()
const sourceOptions = computed(() => {
  const sources = site.newsSources || []
  if (!sources.length) return []
  return [
    ...sources.map((label) => ({ label, value: label })),
    { label: '全部', value: '' },
  ]
})

async function loadNews() {
  loading.value = true
  try {
    const data = await fetchNews({
      page: currentPage.value,
      pageSize: pageSize.value,
      source: selectedSource.value,
    })
    newsList.value = data.list
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function selectSource(value) {
  selectedSource.value = value
  currentPage.value = 1
  loadNews()
}

onMounted(loadNews)

function handlePageChange(page) {
  currentPage.value = page
  loadNews()
}

function goToDetail(id) {
  router.push({ name: 'NewsDetail', params: { id } })
}

// 预留：后续可将 getMockNews 替换为后端接口调用
</script>

<style scoped>
.news-container {
  max-width: 1200px;
  margin: auto;
  padding: 24px 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  font-size: 20px;
  font-weight: bold;
}
.source-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.source-bar button {
  border: 1px solid #dcdfe6;
  background: #fff;
  color: #606266;
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}
.source-bar button.active {
  color: #0b3d73;
  border-color: #0b3d73;
  background: #eef5fb;
}
.news-item {
  padding: 16px 0;
  border-bottom: 1px solid #EBEEF5;
}
.news-item:last-child {
  border-bottom: none;
}
.news-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
  cursor: pointer;
  color: #303133;
}
.news-title:hover {
  color: #409EFF;
}
.news-title a {
  display: block;
  color: inherit;
  text-decoration: none;
}
.news-meta {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}
.news-meta span {
  margin-right: 16px;
}
.news-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
.pagination-bar {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .news-container {
    padding: 8px 0 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    font-size: 18px;
  }

  .news-title {
    font-size: 16px;
    line-height: 1.5;
    word-break: break-word;
  }

  .news-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 4px 12px;
  }

  .news-meta span {
    margin-right: 0;
  }
}
</style>