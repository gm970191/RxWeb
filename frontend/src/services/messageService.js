import { apiRequest } from './apiClient'

export function createMessage(payload) {
  return apiRequest('/api/messages', { method: 'POST', body: payload })
}

export function fetchMessages({ page = 1, pageSize = 10, status = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize })
  if (status) params.set('status', status)
  return apiRequest(`/api/messages?${params.toString()}`)
}

export function replyMessage(id, reply) {
  return apiRequest(`/api/messages/${id}/reply`, { method: 'PUT', body: { reply } })
}

export function fetchMyMessages() {
  return apiRequest('/api/my/messages')
}
