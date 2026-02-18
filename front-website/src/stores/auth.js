import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('website_access_token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function loginWithTelegram(telegramData, orgId) {
    loading.value = true
    try {
      const { data } = await api.post('/website/telegram-login/', {
        ...telegramData,
        org: orgId,
      })
      accessToken.value = data.access
      localStorage.setItem('website_access_token', data.access)
      localStorage.setItem('website_refresh_token', data.refresh)
      user.value = data.user
      return { success: true, user: data.user }
    } catch (err) {
      console.error('Telegram login error:', err)
      return {
        success: false,
        error: err.response?.data?.error || 'Ошибка входа',
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return null
    try {
      const { data } = await api.get('/users/me/', {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })
      user.value = data
      return data
    } catch (err) {
      if (err.response?.status === 401) {
        logout()
      }
      return null
    }
  }

  function logout() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('website_access_token')
    localStorage.removeItem('website_refresh_token')
  }

  return {
    user,
    accessToken,
    loading,
    isAuthenticated,
    loginWithTelegram,
    fetchUser,
    logout,
  }
})
