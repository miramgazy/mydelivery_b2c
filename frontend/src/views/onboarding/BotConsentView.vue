<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 to-indigo-600 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-2 text-center">
        Будьте в курсе!
      </h1>
      
      <p class="text-gray-600 mb-6 text-center text-sm">
        Разрешите уведомления в боте, чтобы получать информацию о заказах и акциях.
      </p>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <div v-if="waitingForBot" class="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-3 rounded-lg mb-4 text-sm text-center">
        <div class="flex items-center justify-center gap-2">
          <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Ожидаем подтверждение в боте...</span>
        </div>
      </div>

      <div class="space-y-4">
        <button
          @click="handleAllow"
          :disabled="loading || waitingForBot"
          class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2"
        >
          <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ loading ? 'Загрузка...' : 'Разрешить' }}</span>
        </button>

        <button
          @click="handleDecline"
          :disabled="loading || waitingForBot"
          class="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95"
        >
          Позже / Отказаться
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import usersService from '@/services/users.service'
import telegramService from '@/services/telegram'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const waitingForBot = ref(false)
let pollingInterval = null

const POLLING_INTERVAL_MS = 5000
const POLLING_MAX_ATTEMPTS = 60 // 5 минут максимум

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  waitingForBot.value = false
}

async function checkSubscription() {
  try {
    const { is_bot_subscribed } = await usersService.checkBotSubscription()
    if (is_bot_subscribed === true) {
      stopPolling()
      await authStore.fetchCurrentUser(true)
      goNext()
    }
  } catch (e) {
    console.error('Check subscription error:', e)
  }
}

function goNext() {
  if (router.currentRoute.value?.query?.from === 'profile') {
    router.replace('/profile')
  } else {
    router.push('/onboarding/address')
  }
}

async function handleAllow() {
  loading.value = true
  error.value = ''

  try {
    const { bot_sync_uuid, bot_username } = await usersService.getBotSyncToken()
    
    if (!bot_username) {
      error.value = 'Бот не настроен для вашей организации. Пропустите этот шаг.'
      loading.value = false
      return
    }

    const botUrl = `https://t.me/${bot_username}?start=${bot_sync_uuid}`
    telegramService.openTelegramLink(botUrl)

    waitingForBot.value = true
    loading.value = false

    let attempts = 0
    pollingInterval = setInterval(async () => {
      attempts++
      if (attempts > POLLING_MAX_ATTEMPTS) {
        stopPolling()
        error.value = 'Время ожидания истекло. Вы можете включить уведомления позже в профиле.'
        return
      }
      await checkSubscription()
    }, POLLING_INTERVAL_MS)
    
    await checkSubscription()
  } catch (err) {
    console.error('Allow error:', err)
    error.value = err.response?.data?.detail || 'Не удалось получить ссылку. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}

async function handleDecline() {
  loading.value = true
  error.value = ''

  try {
    await usersService.declineBotSubscription()
    await authStore.fetchCurrentUser(true)
    goNext()
  } catch (err) {
    console.error('Decline error:', err)
    error.value = err.response?.data?.detail || 'Произошла ошибка'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  stopPolling()
})
</script>
