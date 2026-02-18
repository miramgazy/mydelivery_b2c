<template>
  <div class="flex flex-col min-h-screen pb-24 md:pb-8">
    <header class="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-gray-200">
      <div class="px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-semibold">Оформление заказа</h1>
        <router-link :to="{ path: '/cart', query: $route.query }" class="text-primary text-sm">Корзина</router-link>
      </div>
    </header>

    <main class="flex-1 px-4 py-6">
      <!-- Нет org в URL -->
      <div v-if="!orgId" class="p-4 bg-amber-50 border border-amber-200 rounded-main">
        <p class="text-amber-800 font-medium">Перейдите в меню с главной страницы</p>
        <router-link :to="{ path: '/', query: $route.query }" class="text-primary text-sm mt-2 inline-block underline">На главную</router-link>
      </div>

      <!-- Анонимный пользователь: требуется авторизация -->
      <div v-else-if="!authStore.isAuthenticated" class="space-y-6">
        <div class="p-4 bg-amber-50 border border-amber-200 rounded-main">
          <p class="text-amber-800 font-medium mb-2">Для оформления заказа войдите через Telegram</p>
          <p class="text-sm text-amber-700">После входа вы сможете выбрать адрес доставки и оплату</p>
        </div>
        <div v-if="!botUsername" class="p-4 bg-gray-100 rounded-main text-sm text-secondary/70">
          Вход через Telegram не настроен для этой организации. Обратитесь к администратору.
        </div>
        <div v-else class="flex flex-col items-center py-8">
          <div id="telegram-login-checkout" class="mb-4"></div>
          <router-link
            :to="{ path: '/cart', query: $route.query }"
            class="text-secondary/70 text-sm hover:underline"
          >
            Вернуться в корзину
          </router-link>
        </div>
      </div>

      <!-- Авторизованный пользователь: форма оформления -->
      <div v-else class="space-y-6">
        <p class="text-secondary/70">Выбор адреса и способа оплаты (в разработке)</p>
        <div class="p-4 bg-gray-50 rounded-main text-sm text-secondary/70">
          После подключения API заказов здесь будет форма: адрес доставки, способ оплаты, комментарий.
        </div>
      </div>
    </main>

    <div class="md:hidden h-16"></div>
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

function initTelegramWidget() {
  const container = document.getElementById('telegram-login-checkout')
  if (!container || !botUsername.value || !orgId.value || authStore.isAuthenticated) return
  if (container.children.length) return

  const script = document.createElement('script')
  script.src = 'https://telegram.org/js/telegram-widget.js?22'
  script.setAttribute('data-telegram-login', botUsername.value)
  script.setAttribute('data-size', 'large')
  script.setAttribute('data-radius', '8')
  script.setAttribute('data-onauth', 'onTelegramAuth(user)')
  script.setAttribute('data-request-access', 'write')
  script.async = true
  container.appendChild(script)

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

watch(
  () => [botUsername.value, orgId.value, authStore.isAuthenticated],
  () => initTelegramWidget(),
  { deep: true }
)
</script>
