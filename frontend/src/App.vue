<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organization'
import telegramService from '@/services/telegram'
import authService from '@/services/auth.service'
import { clearTokens } from '@/services/api'
import BottomNav from '@/components/common/BottomNav.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'
import { paletteFromHex, normalizePrimaryHex } from '@/utils/primaryColor'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const organizationStore = useOrganizationStore()

// Multi-bot: блокируем рендер до завершения login в TMA, чтобы запросы (organization, menu, orders)
// не шли со старым токеном первой организации
const tmaInitComplete = ref(false)

// Primary palette from organization.primary_color — применяется ко всем primary-* в TMA
const primaryPaletteStyle = computed(() => {
  const hex = organizationStore.organization?.primary_color
  const normalized = normalizePrimaryHex(hex || null)
  const palette = paletteFromHex(normalized)
  return {
    '--color-primary-50': palette[50],
    '--color-primary-100': palette[100],
    '--color-primary-200': palette[200],
    '--color-primary-300': palette[300],
    '--color-primary-400': palette[400],
    '--color-primary-500': palette[500],
    '--color-primary-600': palette[600],
    '--color-primary-700': palette[700],
    '--color-primary-800': palette[800],
    '--color-primary-900': palette[900],
  }
})

// Скрывать навигацию на странице логина, в админке и onboarding
const showBottomNav = computed(() => {
  return route.name !== 'login' && 
         !route.path.startsWith('/admin') && 
         !route.path.startsWith('/onboarding') &&
         route.name !== 'access-denied'
})

onMounted(async () => {
  try {
    // Инициализация Telegram
    telegramService.init()

    // Если запущено в Telegram — блокируем рендер до завершения login
    if (telegramService.isInTelegram()) {
      const tgUser = telegramService.getUser()
      if (tgUser) {
        console.log('TG User:', tgUser.id)

        // Multi-bot: очищаем старый токен и сторы, чтобы запросы не шли с данными первой организации
        clearTokens()
        authStore.$patch({ user: null })
        organizationStore.$patch({ organization: null })

        // B2C multi-bot: всегда делаем Telegram login при открытии TMA.
        // initData содержит информацию о боте — бэкенд определит организацию.
        let loginResult = await authStore.login()

        if (authStore.isAuthenticated) {
          organizationStore.fetchOrganization().catch(() => {})
        }

        if (!loginResult.success) {
          console.error('Login failed:', loginResult.message)
          if (loginResult.error?.includes('заблокирован') || loginResult.error?.includes('blocked')) {
            router.push({ name: 'access-denied', query: { id: tgUser.id } })
          }
        } else {
          if (authStore.isAuthenticated) {
            const user = authStore.user
            if (!user?.phone) {
              router.push('/onboarding/welcome')
              tmaInitComplete.value = true
              return
            }
            if (!user?.addresses || user.addresses.length === 0) {
              router.push('/onboarding/address')
              tmaInitComplete.value = true
              return
            }
            if (!user?.terminals || user.terminals.length === 0) {
              router.push('/onboarding/terminal')
              tmaInitComplete.value = true
              return
            }
          }
        }
      }
      tmaInitComplete.value = true
    } else {
      // Не в Telegram — сразу показываем контент
      tmaInitComplete.value = true

      if (authService.isAuthenticated()) {
        if (!authStore.isAuthenticated) {
          await authStore.fetchCurrentUser()
        }
        if (authStore.isAuthenticated) {
          organizationStore.fetchOrganization().catch(() => {})
          const user = authStore.user
          const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
          if (route.name === 'login') {
            router.push(isAdmin ? '/admin' : '/')
          } else if (route.name === 'home' && isAdmin) {
            router.push('/admin')
          }
        }
      } else if (route.name !== 'login' && route.name !== 'access-denied') {
        router.push('/login')
      }
    }
  } catch (err) {
    console.error('App Init Error:', err)
    tmaInitComplete.value = true
  }
})
</script>

<template>
  <div class="app-container" :style="primaryPaletteStyle">
    <!-- Multi-bot: в TMA не рендерим контент до завершения login, чтобы не было запросов со старым токеном -->
    <div v-if="!tmaInitComplete" class="flex items-center justify-center min-h-screen">
      <div class="animate-spin w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full"></div>
    </div>
    <template v-else>
      <router-view></router-view>
      <BottomNav v-if="showBottomNav" />
    </template>
    <ToastNotification />
  </div>
</template>

<style>
.app-container {
  width: 100%;
  min-height: 100vh;
  background: var(--tg-theme-bg-color, #fff);
  color: var(--tg-theme-text-color, #000);
}
</style>