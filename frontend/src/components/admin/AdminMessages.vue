<template>
  <div>
    <div class="admin-toolbar">
      <el-radio-group v-model="status" @change="handleFilter">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="pending">待回复 {{ pending }}</el-radio-button>
        <el-radio-button label="replied">已回复</el-radio-button>
      </el-radio-group>
    </div>
    <div class="table-scroll">
      <el-table :data="messageList" :loading="loading" style="width: 100%; min-width: 760px">
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="subject" label="主题" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'replied' ? 'success' : 'warning'" size="small">
              {{ row.status === 'replied' ? '已回复' : '待回复' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="openReply(row)">查看/回复</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="total"
      :small="true"
      layout="prev, pager, next"
      @current-change="loadMessages"
      class="admin-pagination"
    />

    <el-dialog v-model="dialogVisible" title="留言详情" width="600px">
      <div v-if="current">
        <p><strong>姓名：</strong>{{ current.name }}</p>
        <p><strong>邮箱：</strong>{{ current.email }}</p>
        <p><strong>时间：</strong>{{ current.created_at }}</p>
        <p><strong>主题：</strong>{{ current.subject }}</p>
        <p class="message-body">{{ current.content }}</p>
        <div v-if="current.reply" class="reply-box">
          <strong>已回复（{{ current.replied_at }}）</strong>
          <p>{{ current.reply }}</p>
        </div>
        <el-input v-model="replyText" type="textarea" :rows="4" placeholder="请输入回复内容，将保存在后台供后续跟进" />
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleReply">保存回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchMessages, replyMessage } from '../../services/messageService'

const messageList = ref([])
const total = ref(0)
const pending = ref(0)
const page = ref(1)
const pageSize = ref(10)
const status = ref('all')
const loading = ref(false)
const dialogVisible = ref(false)
const current = ref(null)
const replyText = ref('')

async function loadMessages() {
  loading.value = true
  try {
    const data = await fetchMessages({
      page: page.value,
      pageSize: pageSize.value,
      status: status.value === 'all' ? '' : status.value,
    })
    messageList.value = data.list
    total.value = data.total
    pending.value = data.pending
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  page.value = 1
  loadMessages()
}

function openReply(row) {
  current.value = { ...row }
  replyText.value = row.reply || ''
  dialogVisible.value = true
}

async function handleReply() {
  if (!replyText.value.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  try {
    const data = await replyMessage(current.value.id, replyText.value.trim())
    ElMessage.success('回复已保存')
    current.value = { ...current.value, ...data }
    dialogVisible.value = false
    await loadMessages()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.message-body {
  padding: 12px;
  background: #f4f7fb;
  border-radius: 8px;
  white-space: pre-line;
  line-height: 1.7;
}

.reply-box {
  margin: 16px 0;
  padding: 12px;
  background: #f0f9eb;
  border-radius: 8px;
}

.reply-box p {
  margin: 8px 0 0;
  white-space: pre-line;
}
</style>
