<template>
  <div class="flex flex-col min-h-screen pb-20 md:pb-0">
    <header class="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-gray-200">
      <div class="px-4 py-3">
        <h1 class="text-lg font-semibold">Профиль</h1>
      </div>
    </header>

    <main class="flex-1 px-4 py-6">
      <div v-if="authStore.isAuthenticated" class="space-y-6">
        <div class="flex items-center gap-4 p-4 bg-white rounded-main border border-gray-100">
          <div class="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center">
            <span class="text-xl font-bold text-primary">
              {{ userInitials }}
            </span>
          </div>
          <div>
            <h2 class="font-semibold">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</h2>
            <p class="text-sm text-secondary/70">@{{ authStore.user?.username || 'user' }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <router-link
            to="/addresses"
            class="flex items-center justify-between p-4 bg-white rounded-main border border-gray-100"
          >
            <span>Мои адреса</span>
            <svg class="w-5 h-5 text-secondary/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
          <router-link
            to="/orders"
            class="flex items-center justify-between p-4 bg-white rounded-main border border-gray-100"
          >
            <span>История заказов</span>
            <svg class="w-5 h-5 text-secondary/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>

        <button
          @click="authStore.logout()"
          class="w-full py-3 rounded-main border border-red-200 text-red-600 font-medium"
        >
          Выйти
        </button>
      </div>

      <div v-else class="flex flex-col items-center py-12">
        <p class="text-secondary/70 mb-6 text-center">Войдите через Telegram для доступа к адресам и заказам</p>
        <div id="telegram-login-widget"></div>
      </div>
    </main>

    <!-- Mobile Tab Bar -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom z-50">
      <div class="flex justify-around py-2">
        <router-link :to="{ path: '/', query: $route.query }" class="flex flex-col items-center gap-1 px-6 py-2 text-secondary/60">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span class="text-xs">Меню</span>
        </router-link>
        <router-link :to="{ path: '/cart', query: $route.query }" class="flex flex-col items-center gap-1 px-6 py-2 text-secondary/60">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span class="text-xs">Корзина</span>
        </router-link>
        <router-link :to="{ path: '/profile', query: $route.query }" class="flex flex-col items-center gap-1 px-6 py-2 text-primary">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-xs">Профиль</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useWebsiteStore } from '@/stores/website'
import { useRoute } from 'vue-router'

const route = useRoute()
const authStore = useAuthStore()
const websiteStore = useWebsiteStore()

const orgId = computed(() => route.query.org || import.meta.env.VITE_ORG_ID || '')
const botUsername = computed(() => websiteStore.organization?.bot_username?.replace('@', '') || '')

const userInitials = computed(() => {
  const u = authStore.user
  if (!u) return '?'
  const f = (u.first_name || '')[0] || ''
  const l = (u.last_name || '')[0] || ''
  return (f + l).toUpperCase() || '?'
})

function initTelegramWidget() {
  if (!botUsername.value || !orgId.value) return
  if (document.getElementById('telegram-login-widget').children.length) return

  const script = document.createElement('script')
  script.src = 'https://telegram.org/js/telegram-widget.js?22'
  script.setAttribute('data-telegram-login', botUsername.value)
  script.setAttribute('data-size', 'large')
  script.setAttribute('data-radius', '8')
  script.setAttribute('data-onauth', 'onTelegramAuth(user)')
  script.setAttribute('data-request-access', 'write')
  script.async = true
  document.getElementById('telegram-login-widget').appendChild(script)

  window.onTelegramAuth = async (user) => {
    const result = await authStore.loginWithTelegram(user, orgId.value)
    if (result.success) {
      await authStore.fetchUser()
    }
  }
}

onMounted(() => {
  if (!authStore.isAuthenticated) {
    authStore.fetchUser()
  }
  initTelegramWidget()
})

watch([botUsername, orgId], () => {
  if (authStore.isAuthenticated) return
  initTelegramWidget()
})
</script>
