<template>
  <div>
    <h1>公司简介</h1>
    <p>这是一家有着悠久历史的公司，专注于各类产品的研发与销售。</p>
    <h2>新闻：30 周年庆典</h2>
    <p>我们即将举办 30 周年庆典活动，欢迎大家参加！</p>
    <h2>产品展示</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="product in products" :key="product.id">
        <el-card>
          <div>{{ product.name }}</div>
        </el-card>
      </el-col>
    </el-row>
    <h2>联系方式</h2>
    <p>电话：123-456-7890</p>
    <p>邮箱：contact@company.com</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Home',
  setup() {
    const products = ref([])

    onMounted(async () => {
      try {
        const response = await fetch('http://localhost:5000/products')
        products.value = await response.json()
      } catch (error) {
        console.error('获取产品数据失败:', error)
      }
    })

    return {
      products
    }
  }
}
</script>