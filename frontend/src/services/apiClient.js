const TOKEN_KEY = 'rxweb_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export async function apiRequest(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let body = options.body
  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }

  const resp = await fetch(path, { ...options, headers, body })
  let data = null
  try {
    data = await resp.json()
  } catch {
    data = null
  }

  if (resp.status === 401) {
    setToken('')
    localStorage.removeItem('rxweb_username')
    localStorage.removeItem('rxweb_email')
    localStorage.removeItem('rxweb_name')
    localStorage.removeItem('rxweb_role')
    throw new Error((data && data.detail) || (data && data.message) || '请先登录')
  }

  if (resp.status === 403) {
    throw new Error((data && data.detail) || (data && data.message) || '没有权限')
  }

  if (!resp.ok) {
    throw new Error((data && (data.message || data.detail)) || '请求失败')
  }
  if (data && typeof data.code === 'number' && data.code !== 0) {
    throw new Error(data.message || '请求失败')
  }
  return data && Object.prototype.hasOwnProperty.call(data, 'data') ? data.data : data
}
