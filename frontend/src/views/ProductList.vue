<template>
  <div class="product-list-container">
    <div class="product-layout">
      <aside class="catalog" aria-label="产品目录">
        <button
          v-for="cat in categories"
          :key="cat"
          type="button"
          :class="{ active: selectedCategory === cat }"
          @click="selectCategory(cat)"
        >
          {{ cat }}
        </button>
      </aside>
      <div class="product-main">
        <div class="filter-bar">
          <el-select v-model="selectedCategory" placeholder="请选择分类" class="category-select" @change="onCategoryChange">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </div>
        <el-row :gutter="16">
          <el-col v-for="item in pagedProducts" :key="item.id" :xs="24" :sm="12" :md="8" :lg="8" :xl="6">
            <el-card class="product-card">
              <router-link :to="{ name: 'ProductDetail', params: { id: item.id } }">
                <img :src="item.image" class="product-image clickable" />
              </router-link>
              <div class="product-info">
                <h3>{{ item.name }}</h3>
                <p class="desc">{{ item.description }}</p>
                <div class="meta-row">
                  <router-link :to="{ name: 'ProductDetail', params: { id: item.id } }" class="detail-link">详情</router-link>
                  <span class="price">{{ formatPrice(item.price) }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <div class="pagination-bar">
          <el-pagination
            background
            :small="true"
            layout="prev, pager, next"
            :pager-count="5"
            :total="filteredProducts.length"
            :page-size="pageSize"
            v-model:current-page="currentPage"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchProducts, getCategories, getMockProducts } from '../services/productService'
import { formatPrice } from '../utils/price'

const products = ref([])
const categories = ref([])
const selectedCategory = ref('全部')
const currentPage = ref(1)
const pageSize = 8

onMounted(async () => {
  try {
    products.value = await fetchProducts()
  } catch {
    products.value = await getMockProducts()
  }
  categories.value = ['全部', ...(await getCategories())]
})

const filteredProducts = computed(() => {
  if (selectedCategory.value === '全部') return products.value
  return products.value.filter(p => p.category === selectedCategory.value)
})

const pagedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredProducts.value.slice(start, start + pageSize)
})

function onCategoryChange() {
  currentPage.value = 1
}

function selectCategory(category) {
  selectedCategory.value = category
  onCategoryChange()
}

// 预留：后续可将 getMockProducts 替换为后端接口调用
</script>

<style scoped>
.product-list-container {
  max-width: 1200px;
  margin: auto;
  padding: 24px 0;
}
.catalog { display: none; }
.filter-bar { margin-bottom: 16px; }
.product-card { width: 100%; }
.product-image { width: 100%; height: 160px; object-fit: cover; border-radius: 6px; transition: box-shadow 0.2s; }
.product-image.clickable { cursor: pointer; }
.product-image.clickable:hover { box-shadow: 0 2px 12px rgba(64,158,255,0.18); }
.product-info { padding: 8px 0; position: relative; }
.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
}
.detail-link {
  color: #409EFF;
  font-size: 14px;
  text-decoration: underline;
  cursor: pointer;
  white-space: nowrap;
}
.detail-link:hover {
  color: #66b1ff;
}
.price { color: #e4393c; font-weight: bold; white-space: nowrap; }
.desc {
  color: #888;
  font-size: 13px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.pagination-bar { margin-top: 24px; text-align: center; }

@media (min-width: 1100px) {
  .product-list-container {
    max-width: 1320px;
  }

  .product-layout {
    display: grid;
    grid-template-columns: 232px minmax(0, 1fr);
    gap: 24px;
    align-items: start;
  }

  .catalog {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 8px 24px rgba(11, 61, 115, 0.06);
  }

  .catalog button {
    padding: 8px 12px;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: #303133;
    font-size: 14px;
    line-height: 1.45;
    text-align: left;
    cursor: pointer;
  }

  .catalog button:hover {
    background: rgba(11, 61, 115, 0.08);
  }

  .catalog button.active {
    background: #0b3d73;
    color: #fff;
  }

  .filter-bar {
    display: none;
  }
}

@media (max-width: 768px) {
  .product-list-container {
    padding: 8px 0 16px;
  }

  .filter-bar,
  .category-select {
    width: 100%;
  }

  .product-card {
    margin-bottom: 16px;
  }

  .product-image {
    height: 180px;
  }
}
</style> 