<template>
  <div class="account-page">
    <div class="account-header">
      <div>
        <h1>我的留言</h1>
        <p>使用 {{ auth.email }} 提交的留言和回复会显示在这里。</p>
      </div>
      <el-button @click="handleLogout">退出登录</el-button>
    </div>
    <el-empty v-if="!loading && !list.length" description="还没有留言。可到“联系我们”提交。" />
    <el-card v-for="item in list" :key="item.id" class="message-card">
      <div class="message-meta">
        <strong>{{ item.subject }}</strong>
        <el-tag :type="item.status === 'replied' ? 'success' : 'warning'" size="small">
          {{ item.status === 'replied' ? '已回复' : '待回复' }}
        </el-tag>
      </div>
      <p class="time">{{ item.created_at }}</p>
      <p class="body">{{ item.content }}</p>
      <div v-if="item.reply" class="reply">
        <strong>管理员回复（{{ item.replied_at }}）</strong>
        <p>{{ item.reply }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { fetchMyMessages } from '../services/messageService'

const auth = useAuthStore()
const router = useRouter()
const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await fetchMyMessages()
    list.value = (data && data.list) || []
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(load)
</script>

<style scoped>
.account-page {
  max-width: 800px;
  margin: 24px auto;
}

.account-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.account-header h1 {
  margin: 0 0 6px;
}

.account-header p {
  margin: 0;
  color: #606266;
}

.message-card {
  margin-bottom: 12px;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.time {
  color: #909399;
  font-size: 13px;
}

.body,
.reply p {
  white-space: pre-line;
  line-height: 1.7;
}

.reply {
  margin-top: 12px;
  padding: 12px;
  background: #f0f9eb;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .account-header {
    flex-direction: column;
  }
}
</style>
