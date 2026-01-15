<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <ToastNotification />
    <!-- Browser mode - always show router -->
    <router-view v-if="!isInTelegram" />
    
    <!-- Telegram mode below -->
    <template v-else>
      <!-- Проверка доступа -->
      <CheckingAccess v-if="isCheckingAccess" />
      
      <!-- Доступ запрещен -->
      <AccessDenied
        v-else-if="!hasAccess && accessCheckResult"
        :message="accessCheckResult.message"
        :reason="accessCheckResult.reason"
        :telegram-id="telegramId"
      />
      
      <!-- Приложение (если доступ есть и авторизован) -->
      <template v-else-if="isAuthenticated">
        <div class="pb-20">
          <router-view />
          <BottomNav v-if="!isAdminPath" />
        </div>
      </template>
      
      <!-- Экран входа (если доступ есть, но не авторизован) -->
      <div v-else class="min-h-screen flex items-center justify-center">
        <div class="text-center">
          <h2 class="text-xl font-semibold mb-4">Выполняется вход...</h2>
          <div class="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import CheckingAccess from '@/components/auth/CheckingAccess.vue'
import AccessDenied from '@/components/auth/AccessDenied.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'
import BottomNav from '@/components/common/BottomNav.vue'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isCheckingAccess = ref(true)
const telegramId = ref(null)

const hasAccess = computed(() => authStore.hasAccess)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const accessCheckResult = computed(() => authStore.accessCheckResult)
const isInTelegram = computed(() => telegramService.isInTelegram())
const isAdminPath = computed(() => router.currentRoute.value.path.startsWith('/admin'))

onMounted(async () => {
  alert('Инициализация приложения...')
  try {
    // 1. Инициализируем Telegram
    alert('Шаг 1: Инфо Telegram...')
    telegramService.init()
    
    // Проверяем что запущены в Telegram
    if (!telegramService.isInTelegram()) {
      alert('Ошибка: Режим браузера, а не Telegram')
      isCheckingAccess.value = false
      return
    }

    // Получаем Telegram ID
    const tgUser = telegramService.getUser()
    telegramId.value = tgUser?.id
    alert(`Шаг 2: Ваш ID: ${tgUser?.id}`)

    if (authStore.isAuthenticated) {
      alert('Шаг 2.5: Восстанавливаем сессию...')
      const currentUser = await authStore.fetchCurrentUser()
      if (currentUser) {
        alert('Успех: Сессия восстановлена!')
        isCheckingAccess.value = false
        if (router.currentRoute.value.path === '/login' || router.currentRoute.value.path === '/checking-access') {
           router.push('/')
        }
        return
      }
    }

    // 2. Проверяем доступ
    alert('Шаг 3: Запрос к API (checkAccess)...')
    await authStore.checkAccess()
    alert(`Результат доступа: ${authStore.hasAccess ? 'РАЗРЕШЕНО' : 'ЗАПРЕЩЕНО'}`)

    if (!authStore.hasAccess) {
      isCheckingAccess.value = false
      return
    }

    // 3. Доступ есть - пытаемся войти
    alert('Шаг 4: Попытка входа (login)...')
    const loginResult = await authStore.login()
    alert(`Результат входа: ${loginResult.success ? 'УСПЕХ' : 'ОШИБКА'}`)

    if (loginResult.success) {
      // Успешный вход - загружаем данные пользователя
      console.log('Login successful')
      await authStore.fetchCurrentUser()
      
      // Показываем приветствие
      if (loginResult.message) {
        notificationStore.show(loginResult.message)
      }
      
      // Навигация на главную
      router.push('/')
    } else {
      // Ошибка входа - это не должно случиться если checkAccess прошел
      console.error('Login failed despite access check:', loginResult)
      
      // Если это ошибка USER_NOT_FOUND - обновляем результат проверки
      if (loginResult.code === 'USER_NOT_FOUND') {
        authStore.accessCheckResult = {
          has_access: false,
          message: loginResult.message,
          reason: 'not_found',
          telegram_id: loginResult.telegram_id
        }
      }
    }
    console.log('App initialized successfully')
  } catch (error) {
    console.error('Initialization error:', error)
    const errorMsg = error.message || 'Неизвестная ошибка'
    const errorStack = error.stack || ''
    alert(`КРИТИЧЕСКАЯ ОШИБКА TMA: ${errorMsg}\n${errorStack.substring(0, 50)}`)
  } finally {
    isCheckingAccess.value = false
  }
})
</script>

<style>
/* Используем CSS переменные от Telegram */
:root {
  --tg-theme-bg-color: #ffffff;
  --tg-theme-text-color: #000000;
  --tg-theme-hint-color: #999999;
  --tg-theme-link-color: #2481cc;
  --tg-theme-button-color: #5288c1;
  --tg-theme-button-text-color: #ffffff;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}

/* Отключаем выделение для лучшего UX в Telegram */
* {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
}

/* Safe area для iPhone */
#app {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}
</style>