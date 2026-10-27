<template>
  <div>
    <h1>产品介绍</h1>
    <div v-for="category in categories" :key="category">
      <h2>{{ category }}</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="product in getProductsByCategory(category)" :key="product.id">
          <el-card>
            <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }">
              <img :src="`/img/${product.image}`" :alt="product.name" style="width: 100%; height: auto; max-width: 200px;" />
              {{ product.name }}
            </router-link>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElRow, ElCol, ElCard } from 'element-plus'

export default {
  name: 'Products',
  setup() {
    const products = ref([])
    const route = useRoute()
    const router = useRouter()

    onMounted(async () => {
      try {
        const response = await fetch('http://localhost:5000/products')
        const data = await response.json()
        if (Array.isArray(data)) {
          products.value = data
        } else {
          console.error('获取的数据不是数组:', data)
        }
      } catch (error) {
        console.error('获取产品数据失败:', error)
      }
    })

    const categories = computed(() => {
      if (Array.isArray(products.value)) {
        const categorySet = new Set(products.value.map(product => product.category))
        return Array.from(categorySet)
      } else {
        return []
      }
    })

    const getProductsByCategory = (category) => {
      if (Array.isArray(products.value)) {
        return products.value.filter(product => product.category === category)
      } else {
        return []
      }
    }

    return {
      products,
      categories,
      getProductsByCategory,
      ElRow,
      ElCol,
      ElCard
    }
  }
}
</script>