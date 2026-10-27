<template>
  <div>
    <div class="admin-toolbar">
      <div class="log-legend">记录登录、内容变更和留言处理，文件副本在 logs/rxweb-ops.log</div>
      <div class="admin-search">
        <el-input v-model="keyword" placeholder="搜索操作人/动作/详情/IP" @keyup.enter="handleSearch" />
        <el-button @click="handleSearch">搜索</el-button>
      </div>
    </div>
    <div class="table-scroll">
      <el-table :data="logList" :loading="loading" style="width: 100%; min-width: 860px">
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column label="动作" width="130">
          <template #default="{ row }">{{ actionLabel(row.action) }}</template>
        </el-table-column>
        <el-table-column label="结果" width="90">
          <template #default="{ row }">
            <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">
              {{ row.result === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" />
        <el-table-column prop="ip" label="IP" width="140" />
      </el-table>
    </div>
    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      :small="true"
      layout="prev, pager, next"
      @current-change="loadLogs"
      class="admin-pagination"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchLogs } from '../../services/logService'

const labels = {
  login_success: '登录成功',
  login_fail: '登录失败',
  logout: '退出登录',
  register: '用户注册',
  password_reset_request: '申请重置密码',
  password_reset: '密码已重置',
  news_create: '新增新闻',
  news_update: '编辑新闻',
  news_delete: '删除新闻',
  product_create: '新增产品',
  product_update: '编辑产品',
  product_delete: '删除产品',
  message_create: '访客留言',
  message_reply: '回复留言',
}

const logList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const loading = ref(false)

function actionLabel(action) {
  return labels[action] || action
}

async function loadLogs() {
  loading.value = true
  try {
    const data = await fetchLogs({ page: page.value, pageSize: pageSize.value, keyword: keyword.value })
    logList.value = data.list
    total.value = data.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadLogs()
}

onMounted(loadLogs)
</script>

<style scoped>
.log-legend {
  color: #606266;
  font-size: 13px;
}
</style>
