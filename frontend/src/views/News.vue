<template>
  <div>
    <h1>新闻动态</h1>
    <input v-model="searchQuery" placeholder="搜索新闻" />
    <ul>
      <li v-for="item in filteredNews" :key="item.id">
        <h2>{{ item.title }}</h2>
        <p>{{ item.content }}</p>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'News',
  setup() {
    const news = ref([])
    const searchQuery = ref('')

    onMounted(async () => {
      try {
        const response = await fetch('http://localhost:5000/news')
        news.value = await response.json()
      } catch (error) {
        console.error('获取新闻数据失败:', error)
      }
    })

    const filteredNews = computed(() => {
      return news.value.filter(item => 
        item.title && item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
        item.content && item.content.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    return {
      news,
      searchQuery,
      filteredNews
    }
  }
}
</script>