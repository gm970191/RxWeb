import { apiRequest } from './apiClient'

const mockProducts = [
  { id: 1, name: '智能手表', price: 399, category: '智能设备', image: 'https://picsum.photos/240/160?1', description: '健康监测，消息提醒，超长续航。' },
  { id: 2, name: '蓝牙耳机', price: 199, category: '音频设备', image: 'https://picsum.photos/240/160?2', description: '高清音质，降噪体验，舒适佩戴。' },
  { id: 3, name: '机械键盘', price: 499, category: '外设', image: 'https://picsum.photos/240/160?3', description: 'RGB背光，手感极佳，耐用轴体。' },
]

export function getMockProducts() {
  return Promise.resolve(mockProducts)
}

export async function fetchProducts(keyword = '') {
  const qs = keyword ? `?keyword=${encodeURIComponent(keyword)}` : ''
  return apiRequest(`/api/products${qs}`)
}

export async function fetchProductDetail(id) {
  return apiRequest(`/api/products/${id}`)
}

export async function createProduct(product) {
  return apiRequest('/api/products', { method: 'POST', body: product })
}

export async function updateProduct(id, product) {
  return apiRequest(`/api/products/${id}`, { method: 'PUT', body: product })
}

export async function deleteProduct(id) {
  return apiRequest(`/api/products/${id}`, { method: 'DELETE' })
}

export async function getCategories() {
  try {
    const products = await fetchProducts()
    return [...new Set((products || []).map((p) => p.category).filter(Boolean))]
  } catch {
    return [...new Set(mockProducts.map((p) => p.category))]
  }
}
