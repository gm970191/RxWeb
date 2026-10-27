<template>
  <div>
    <div class="admin-toolbar">
      <el-button type="primary" @click="openEditDialog()">新增产品</el-button>
      <div class="admin-search">
        <el-input v-model="keyword" placeholder="搜索产品名称/分类" @keyup.enter="handleSearch" />
        <el-button @click="handleSearch">搜索</el-button>
      </div>
    </div>
    <div class="table-scroll">
      <el-table :data="productList" :loading="loading" style="width: 100%; min-width: 760px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="图片" width="90">
          <template #default="{ row }">
            <img v-if="row.image" :src="row.image" class="thumb" alt="" />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editDialogVisible" :title="editForm.id ? '编辑产品' : '新增产品'" width="560px">
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="80px" class="admin-form">
        <el-form-item label="名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input v-model="editForm.price" placeholder="请输入价格" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="editForm.category" placeholder="例如：智能设备" />
        </el-form-item>
        <el-form-item label="图片" prop="image">
          <el-input v-model="editForm.image" placeholder="请输入图片 URL" />
          <img v-if="editForm.image" :src="editForm.image" class="preview" alt="" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="4" placeholder="请输入产品描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createProduct, deleteProduct, fetchProducts, updateProduct } from '../../services/productService'

const productList = ref([])
const keyword = ref('')
const loading = ref(false)
const editDialogVisible = ref(false)
const editForm = reactive({ id: null, name: '', price: '', category: '', image: '', description: '' })
const formRef = ref()

const rules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  category: [{ required: true, message: '请输入分类', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
}

async function loadProducts() {
  loading.value = true
  try {
    productList.value = await fetchProducts(keyword.value)
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function openEditDialog(row) {
  if (row) {
    Object.assign(editForm, row)
  } else {
    Object.assign(editForm, { id: null, name: '', price: '', category: '', image: '', description: '' })
  }
  editDialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  try {
    if (editForm.id) {
      await updateProduct(editForm.id, editForm)
      ElMessage.success('保存成功')
    } else {
      await createProduct(editForm)
      ElMessage.success('新增成功')
    }
    editDialogVisible.value = false
    await loadProducts()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete(id) {
  ElMessageBox.confirm('确定要删除这个产品吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteProduct(id)
        ElMessage.success('删除成功')
        loadProducts()
      } catch (e) {
        ElMessage.error(e.message)
      }
    })
}

function handleSearch() {
  loadProducts()
}

onMounted(loadProducts)
</script>

<style scoped>
.thumb,
.preview {
  width: 56px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
}

.preview {
  width: 100%;
  height: 140px;
  margin-top: 10px;
}
</style>
