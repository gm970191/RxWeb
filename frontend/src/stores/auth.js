import { defineStore } from 'pinia'
import { fetchMe, login as loginApi, register as registerApi } from '../services/authService'
import { logoutRemote } from '../services/logService'
import { setToken } from '../services/apiClient'

function loadStored() {
  return {
    token: localStorage.getItem('rxweb_token') || '',
    email: localStorage.getItem('rxweb_email') || localStorage.getItem('rxweb_username') || '',
    name: localStorage.getItem('rxweb_name') || '',
    role: localStorage.getItem('rxweb_role') || '',
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    ...loadStored(),
    checked: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.email),
    isAdmin: (state) => state.role === 'admin',
    displayName: (state) => state.name || state.email,
  },
  actions: {
    persist() {
      setToken(this.token)
      if (this.email) localStorage.setItem('rxweb_email', this.email)
      else localStorage.removeItem('rxweb_email')
      if (this.name) localStorage.setItem('rxweb_name', this.name)
      else localStorage.removeItem('rxweb_name')
      if (this.role) localStorage.setItem('rxweb_role', this.role)
      else localStorage.removeItem('rxweb_role')
      localStorage.removeItem('rxweb_username')
    },
    applySession(data) {
      this.token = data.token || this.token
      this.email = data.email || ''
      this.name = data.name || ''
      this.role = data.role || 'user'
      this.persist()
    },
    clearSession() {
      this.token = ''
      this.email = ''
      this.name = ''
      this.role = ''
      this.persist()
    },
    async login(email, password) {
      const data = await loginApi(email, password)
      this.applySession(data)
    },
    async register(payload) {
      const data = await registerApi(payload)
      this.applySession(data)
    },
    async hydrate() {
      if (!this.token) {
        this.clearSession()
        this.checked = true
        return
      }
      try {
        const me = await fetchMe()
        this.email = me.email
        this.name = me.name || ''
        this.role = me.role || 'user'
        this.persist()
      } catch {
        this.clearSession()
      } finally {
        this.checked = true
      }
    },
    async logout() {
      try {
        if (this.token) await logoutRemote()
      } catch {
        // 退出仍应清掉本地会话
      }
      this.clearSession()
    },
    homePath() {
      return this.isAdmin ? '/admin/news' : '/account'
    },
  },
})
