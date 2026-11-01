<template>
  <div class="downloads-container page-shell">
    <PageBanner title="资源下载" />
    <el-card class="box-card">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入文件名或描述进行搜索"
          clearable
        />
      </div>
      <div class="download-list">
        <article v-for="item in pagedDownloads" :key="item.id || item.name" class="download-item">
          <div class="download-body">
            <h3>{{ item.name }}</h3>
            <p>{{ item.description }}</p>
            <div class="download-meta">
              <span>版本 {{ item.version }}</span>
              <span>{{ item.size }}</span>
              <span>{{ item.date }}</span>
            </div>
          </div>
          <el-button type="primary" @click="handleDownload">下载</el-button>
        </article>
        <el-empty v-if="!pagedDownloads.length" description="没有匹配的资料" />
      </div>
    </el-card>

    <div class="pagination-bar">
      <el-pagination
        background
        :small="true"
        layout="prev, pager, next"
        :pager-count="5"
        :total="filteredDownloads.length"
        :page-size="pageSize"
        v-model:current-page="currentPage"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import PageBanner from '../components/PageBanner.vue'
import { getMockDownloads } from '../services/downloadService'

const downloadList = ref([])
const currentPage = ref(1)
const pageSize = 10
const searchQuery = ref('')

onMounted(async () => {
  downloadList.value = await getMockDownloads()
})

const filteredDownloads = computed(() => {
  if (!searchQuery.value) {
    return downloadList.value
  }
  return downloadList.value.filter(item => {
    const query = searchQuery.value.toLowerCase()
    return (
      item.name.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query)
    )
  })
})

const pagedDownloads = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredDownloads.value.slice(start, start + pageSize)
})

// 搜索时重置分页到第一页
watch(searchQuery, () => {
  currentPage.value = 1
})

const handleDownload = () => {
  // 实际下载逻辑会在这里实现
  ElMessage.success('开始下载...（模拟）')
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 8px;
}
.pagination-bar {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
.download-list {
  display: flex;
  flex-direction: column;
}
.download-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 18px 0;
  border-bottom: 1px solid #ebeef5;
}
.download-item:last-of-type {
  border-bottom: none;
}
.download-body {
  min-width: 0;
  flex: 1;
}
.download-body h3 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  word-break: break-word;
}
.download-body p {
  margin: 0 0 10px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}
.download-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  color: #909399;
  font-size: 13px;
}
.download-item :deep(.el-button) {
  flex: none;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .download-item {
    flex-direction: column;
    gap: 12px;
  }

  .download-item :deep(.el-button) {
    width: 100%;
  }
}
</style> 