import { apiRequest } from './apiClient'
import { site } from '../site'

// 接口不可用时首页兜底，内容随站点切换
const mockNews = site.fallbackNews

export function getMockNews() {
  return Promise.resolve(mockNews)
}

export async function fetchNews({ page = 1, pageSize = 10, keyword = '', source = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize })
  if (keyword) params.set('keyword', keyword)
  if (source) params.set('source', source)
  return apiRequest(`/api/news?${params.toString()}`)
}

export async function fetchNewsDetail(id) {
  return apiRequest(`/api/news/${id}`)
}

export async function createNews(news) {
  return apiRequest('/api/news', { method: 'POST', body: news })
}

export async function updateNews(id, news) {
  return apiRequest(`/api/news/${id}`, { method: 'PUT', body: news })
}

export async function deleteNews(id) {
  return apiRequest(`/api/news/${id}`, { method: 'DELETE' })
}
