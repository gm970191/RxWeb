import { apiRequest } from './apiClient'
import { site } from '../site'

const mockProducts = site.fallbackProducts

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
