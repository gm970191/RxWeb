<template>
  <div>
    <div class="admin-toolbar">
      <el-button type="primary" @click="openEditDialog()">新增新闻</el-button>
      <div class="admin-search">
        <el-input v-model="keyword" placeholder="搜索标题/摘要/来源" @keyup.enter="handleSearch" />
        <el-button @click="handleSearch">搜索</el-button>
      </div>
    </div>
    <div class="table-scroll">
      <el-table :data="newsList" :loading="loading" style="width: 100%; min-width: 760px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="summary" label="摘要" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">预览</el-button>
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
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
      @current-change="loadNews"
      class="admin-pagination"
    />

    <el-dialog v-model="editDialogVisible" :title="editForm.id ? '编辑新闻' : '新增新闻'" width="560px">
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="80px" class="admin-form">
        <el-form-item label="标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="editForm.date" type="date" value-format="YYYY-MM-DD" placeholder="请选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="editForm.source" placeholder="请输入来源" />
        </el-form-item>
        <el-form-item label="摘要" prop="summary">
          <el-input v-model="editForm.summary" type="textarea" placeholder="请输入摘要" />
        </el-form-item>
        <el-form-item label="正文" prop="content">
          <el-input v-model="editForm.content" type="textarea" :rows="6" placeholder="请输入正文" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="新闻详情" width="600px">
      <div v-if="detailData">
        <h2>{{ detailData.title }}</h2>
        <p><strong>日期：</strong>{{ detailData.date }}</p>
        <p><strong>来源：</strong>{{ detailData.source }}</p>
        <p><strong>摘要：</strong>{{ detailData.summary }}</p>
        <div style="margin-top: 16px; white-space: pre-line;">{{ detailData.content }}</div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createNews, deleteNews, fetchNews, fetchNewsDetail, updateNews } from '../../services/newsService'

const newsList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const loading = ref(false)
const editDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const editForm = reactive({ id: null, title: '', date: '', source: '', summary: '', content: '' })
const detailData = ref({})
const formRef = ref()

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  source: [{ required: true, message: '请输入来源', trigger: 'blur' }],
  summary: [{ required: true, message: '请输入摘要', trigger: 'blur' }],
  content: [{ required: true, message: '请输入正文', trigger: 'blur' }],
}

async function loadNews() {
  loading.value = true
  try {
    const data = await fetchNews({ page: page.value, pageSize: pageSize.value, keyword: keyword.value })
    newsList.value = data.list
    total.value = data.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function openEditDialog(row) {
  if (row) {
    const detail = await fetchNewsDetail(row.id)
    Object.assign(editForm, detail)
  } else {
    Object.assign(editForm, { id: null, title: '', date: '', source: '', summary: '', content: '' })
  }
  editDialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  try {
    if (editForm.id) {
      await updateNews(editForm.id, editForm)
      ElMessage.success('保存成功')
    } else {
      await createNews(editForm)
      ElMessage.success('新增成功')
    }
    editDialogVisible.value = false
    await loadNews()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete(id) {
  ElMessageBox.confirm('确定要删除这条新闻吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteNews(id)
        ElMessage.success('删除成功')
        loadNews()
      } catch (e) {
        ElMessage.error(e.message)
      }
    })
}

async function handleView(row) {
  try {
    detailData.value = await fetchNewsDetail(row.id)
    detailDialogVisible.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function handleSearch() {
  page.value = 1
  loadNews()
}

onMounted(loadNews)
</script>
