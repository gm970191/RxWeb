import { apiRequest } from './apiClient'

export function fetchLogs({ page = 1, pageSize = 20, keyword = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize, keyword })
  return apiRequest(`/api/logs?${params.toString()}`)
}

export function logoutRemote() {
  return apiRequest('/api/auth/logout', { method: 'POST' })
}
