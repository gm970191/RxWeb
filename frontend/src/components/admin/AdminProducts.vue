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
      <el-table :data="pagedProducts" :loading="loading" style="width: 100%; min-width: 860px">
        <el-table-column prop="sort_order" label="排序" width="70" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="图片" width="120">
          <template #default="{ row }">
            <img v-if="row.image && !broken[row.id]" :src="row.image" class="thumb" alt="" @error="broken[row.id] = true" />
            <el-tag v-if="!row.image" type="info" size="small">未配图</el-tag>
            <el-tag v-else-if="broken[row.id]" type="danger" size="small">图片失效</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="分类" width="140" />
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
    <el-pagination
      v-model:current-page="page"
      :page-size="pageSize"
      :total="productList.length"
      :small="true"
      layout="prev, pager, next"
      class="admin-pagination"
    />

    <el-dialog v-model="editDialogVisible" :title="editForm.id ? '编辑产品' : '新增产品'" width="560px">
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="80px" class="admin-form">
        <el-form-item label="名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input v-model="editForm.price" placeholder="数字会显示为金额，文字如「面议」会原样显示" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select
            v-model="editForm.category"
            filterable
            allow-create
            default-first-option
            placeholder="选择已有分类，或输入新分类"
            style="width: 100%"
          >
            <el-option v-for="item in categories" :key="item" :label="item" :value="item" />
          </el-select>
          <p class="field-hint">同一类产品请用完全相同的文字，多一个空格会变成另一个分类。</p>
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="editForm.sort_order" :min="0" :max="999999" :step="1" />
          <p class="field-hint">数字越小越靠前。首页没有指定推荐产品时，取最靠前的几条。</p>
        </el-form-item>
        <el-form-item label="图片" prop="image">
          <el-input v-model="editForm.image" placeholder="站内路径或 http(s) 地址" />
          <div class="image-actions">
            <el-button @click="openLibrary">选择已有图片</el-button>
            <el-button @click="fileInput?.click()">上传图片</el-button>
            <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleUpload" />
          </div>
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

    <el-dialog v-model="libraryVisible" title="本站产品图" width="680px">
      <div class="library-bar">
        <span>没有产品在用的上传图片可以删除。随站点发布的图片请到该站 media/products 目录里处理。</span>
        <el-button @click="fileInput?.click()">上传</el-button>
      </div>
      <div v-if="!images.length" class="library-empty">还没有可选择的图片。</div>
      <div v-else class="image-grid">
        <div
          v-for="item in images"
          :key="item.url"
          class="image-card"
          :class="{ selected: editForm.image === item.url }"
          @click="chooseImage(item)"
        >
          <img :src="item.url" alt="" />
          <div class="image-meta">
            <el-tag v-if="item.used" size="small" type="success">使用中</el-tag>
            <el-tag v-else-if="item.deletable" size="small" type="warning">未使用</el-tag>
            <el-tag v-else size="small" type="info">随站点发布</el-tag>
            <el-button
              v-if="item.deletable"
              link
              type="danger"
              @click.stop="handleDeleteImage(item)"
            >删除</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createProduct, deleteProduct, fetchProducts, updateProduct } from '../../services/productService'
import { deleteProductImage, fetchProductImages, uploadProductImage } from '../../services/mediaService'

const productList = ref([])
const keyword = ref('')
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const broken = reactive({})
const editDialogVisible = ref(false)
const libraryVisible = ref(false)
const images = ref([])
const editForm = reactive({ id: null, name: '', price: '', category: '', image: '', description: '', sort_order: 1 })
const formRef = ref()
const fileInput = ref()

const rules = {
  name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  category: [{ required: true, message: '请选择或输入分类', trigger: 'change' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
}

const categories = computed(() => {
  return [...new Set(productList.value.map((item) => (item.category || '').trim()).filter(Boolean))].sort()
})

const pagedProducts = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return productList.value.slice(start, start + pageSize.value)
})

function nextSortOrder() {
  const values = productList.value.map((item) => Number(item.sort_order) || 0)
  return values.length ? Math.max(...values) + 1 : 1
}

async function loadProducts() {
  loading.value = true
  try {
    productList.value = await fetchProducts(keyword.value)
    Object.keys(broken).forEach((key) => { delete broken[key] })
    const maxPage = Math.max(1, Math.ceil(productList.value.length / pageSize.value))
    if (page.value > maxPage) page.value = maxPage
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function loadImages() {
  const data = await fetchProductImages()
  images.value = (data && data.list) || []
}

function openEditDialog(row) {
  if (row) {
    Object.assign(editForm, row, { sort_order: Number(row.sort_order) || 0 })
  } else {
    Object.assign(editForm, {
      id: null,
      name: '',
      price: '',
      category: '',
      image: '',
      description: '',
      sort_order: nextSortOrder(),
    })
  }
  editDialogVisible.value = true
}

async function openLibrary() {
  libraryVisible.value = true
  try {
    await loadImages()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function chooseImage(item) {
  editForm.image = item.url
  libraryVisible.value = false
}

async function handleUpload(event) {
  const file = event.target.files && event.target.files[0]
  event.target.value = ''
  if (!file) return
  try {
    const data = await uploadProductImage(file)
    editForm.image = data.url
    ElMessage.success('图片已上传')
    if (libraryVisible.value) await loadImages()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDeleteImage(item) {
  try {
    await ElMessageBox.confirm('确定删除这张未使用的图片吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteProductImage(item.name)
    if (editForm.image === item.url) editForm.image = ''
    ElMessage.success('已删除')
    await loadImages()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleSave() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  try {
    const payload = {
      ...editForm,
      category: editForm.category.trim(),
      sort_order: Number(editForm.sort_order) || 0,
    }
    if (editForm.id) {
      await updateProduct(editForm.id, payload)
      ElMessage.success('保存成功')
    } else {
      await createProduct(payload)
      ElMessage.success('新增成功')
    }
    editDialogVisible.value = false
    await loadProducts()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete(id) {
  ElMessageBox.confirm('确定要删除这个产品吗？图片会保留。', '提示', { type: 'warning' })
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
  page.value = 1
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

.field-hint {
  margin: 6px 0 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.image-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.library-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  color: #606266;
  font-size: 13px;
}

.library-empty {
  color: #909399;
  padding: 24px 0;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  max-height: 420px;
  overflow: auto;
}

.image-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 6px;
  cursor: pointer;
}

.image-card.selected {
  border-color: #0b3d73;
}

.image-card img {
  width: 100%;
  height: 72px;
  object-fit: cover;
  border-radius: 4px;
  background: #f4f7fb;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}
</style>
