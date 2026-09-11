import { defineStore } from 'pinia'
import { api } from '~/utils/api'

const KEYS = ['token', 'role', 'user_id', 'username', 'name'] as const

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    role: null as string | null,
    user_id: null as string | null,
    username: null as string | null,
    name: null as string | null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isSuperAdmin: (state) => state.role === 'super_admin',
    isAdmin: (state) => state.role === 'admin',
    /** Landing page for the current role after login. */
    homePath: (state) =>
      state.role === 'super_admin' ? '/superadmin' : `/admin/dashboard/${state.username || ''}`,
  },

  actions: {
    async login(username: string, password: string) {
      const data = await api.post('/api/auth/login', { username, password })
      this.token    = data.access_token
      this.role     = data.role
      this.user_id  = data.user_id
      this.username = data.username
      this.name     = data.name

      if (import.meta.client) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('role', data.role)
        localStorage.setItem('user_id', data.user_id)
        localStorage.setItem('username', data.username)
        localStorage.setItem('name', data.name)
      }
      return data
    },

    logout() {
      for (const k of KEYS) (this as any)[k] = null
      if (import.meta.client) {
        localStorage.clear()
        window.location.href = '/admin/login'
      }
    },

    // Restore the session from localStorage after a page refresh
    init() {
      if (import.meta.client) {
        for (const k of KEYS) (this as any)[k] = localStorage.getItem(k)
      }
    },
  },
})
