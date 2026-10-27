<template>
  <div>
    <h1>{{ product.name }}</h1>
    <img :src="`/img/${product.image}`" :alt="product.name" style="width: 100%; height: auto; max-width: 200px;" />
    <h2>产品参数</h2>
    <p>{{ product.parameters }}</p>
    <h2>产品详述</h2>
    <p>{{ product.description }}</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'ProductDetail',
  setup() {
    const route = useRoute()
    const product = ref({})

    onMounted(async () => {
      try {
        const response = await fetch(`http://localhost:5000/products/${route.params.id}`)
        product.value = await response.json()
      } catch (error) {
        console.error('获取产品详情失败:', error)
      }
    })

    return {
      product
    }
  }
}
</script>