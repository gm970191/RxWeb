import { apiRequest } from './apiClient'

export function fetchProductImages() {
  return apiRequest('/api/media/products')
}

export function uploadProductImage(file) {
  const body = new FormData()
  body.append('file', file)
  return apiRequest('/api/media/products', { method: 'POST', body })
}

export function deleteProductImage(name) {
  return apiRequest(`/api/media/products/${encodeURIComponent(name)}`, { method: 'DELETE' })
}
