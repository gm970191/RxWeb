import { apiRequest } from './apiClient'

export function login(email, password) {
  return apiRequest('/api/auth/login', {
    method: 'POST',
    body: { email, password },
  })
}

export function register({ email, password, name }) {
  return apiRequest('/api/auth/register', {
    method: 'POST',
    body: { email, password, name },
  })
}

export function forgotPassword(email) {
  return apiRequest('/api/auth/forgot-password', {
    method: 'POST',
    body: { email },
  })
}

export function resetPassword(token, password) {
  return apiRequest('/api/auth/reset-password', {
    method: 'POST',
    body: { token, password },
  })
}

export function fetchMe() {
  return apiRequest('/api/auth/me')
}
