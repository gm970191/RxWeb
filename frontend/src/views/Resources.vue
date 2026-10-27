<template>
  <div>
    <h1>资源下载</h1>
    <input v-model="searchQuery" placeholder="搜索资源" />
    <ul>
      <li v-for="resource in filteredResources" :key="resource.id">
        <a :href="resource.url" target="_blank">{{ resource.name }} ({{ resource.type }})</a>
      </li>
    </ul>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'Resources',
  setup() {
    const resources = ref([])
    const searchQuery = ref('')

    onMounted(async () => {
      try {
        const response = await fetch('http://localhost:5000/resources')
        resources.value = await response.json()
      } catch (error) {
        console.error('获取资源数据失败:', error)
      }
    })

    const filteredResources = computed(() => {
      return resources.value.filter(resource => 
        resource.name && resource.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    })

    return {
      resources,
      searchQuery,
      filteredResources
    }
  }
}
</script>