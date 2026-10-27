<template>
  <div class="downloads-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>资源下载</span>
        </div>
      </template>
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="请输入文件名或描述进行搜索"
          clearable
        />
      </div>
      <div class="download-table table-scroll">
        <el-table :data="pagedDownloads" style="width: 100%; min-width: 720px">
          <el-table-column prop="name" label="文件名" width="250" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="version" label="版本" width="100" />
          <el-table-column prop="size" label="大小" width="100" />
          <el-table-column prop="date" label="发布日期" width="120" />
          <el-table-column label="操作" width="120">
            <template #default>
              <el-button type="primary" size="small" @click="handleDownload">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="download-cards">
        <el-card v-for="item in pagedDownloads" :key="item.id || item.name" class="download-card">
          <div class="download-card-title">{{ item.name }}</div>
          <p class="download-card-desc">{{ item.description }}</p>
          <div class="download-card-meta">
            <span>版本 {{ item.version }}</span>
            <span>{{ item.size }}</span>
            <span>{{ item.date }}</span>
          </div>
          <el-button type="primary" size="small" @click="handleDownload">下载</el-button>
        </el-card>
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
import { getMockDownloads } from '../services/downloadService'
import { ElMessage } from 'element-plus'

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
.downloads-container {
  max-width: 1200px;
  margin: auto;
  padding: 24px 0;
}
.card-header {
  font-size: 20px;
  font-weight: bold;
}
.search-bar {
  margin-bottom: 16px;
}
.pagination-bar {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.download-cards {
  display: none;
}

@media (max-width: 768px) {
  .downloads-container {
    padding: 8px 0 16px;
  }

  .download-table {
    display: none;
  }

  .download-cards {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .download-card-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    word-break: break-word;
  }

  .download-card-desc {
    margin: 0 0 10px;
    color: #606266;
    font-size: 14px;
    line-height: 1.5;
  }

  .download-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 12px;
    margin-bottom: 12px;
    color: #909399;
    font-size: 13px;
  }

  .download-card :deep(.el-button) {
    width: 100%;
  }
}
</style> 