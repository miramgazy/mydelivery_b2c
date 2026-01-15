<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Иконка -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/30 mb-4">
          <svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Доступ запрещен
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          {{ message }}
        </p>
      </div>

      <!-- Карточка с информацией -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 mb-4">
        <!-- Для незарегистрированных пользователей -->
        <div v-if="reason === 'not_found'" class="space-y-4">
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 class="font-semibold text-blue-900 dark:text-blue-300 mb-2 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Как получить доступ?
            </h3>
            <ol class="space-y-2 text-sm text-blue-800 dark:text-blue-200">
              <li class="flex items-start">
                <span class="font-semibold mr-2">1.</span>
                <span>Обратитесь к администратору вашей организации</span>
              </li>
              <li class="flex items-start">
                <span class="font-semibold mr-2">2.</span>
                <span>Сообщите ваш Telegram ID</span>
              </li>
              <li class="flex items-start">
                <span class="font-semibold mr-2">3.</span>
                <span>После регистрации перезапустите приложение</span>
              </li>
            </ol>
          </div>

          <!-- Telegram ID -->
          <div v-if="telegramId" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-2">
              Ваш Telegram ID:
            </label>
            <div class="flex items-center gap-2">
              <code class="flex-1 bg-white dark:bg-gray-800 px-3 py-2 rounded border border-gray-200 dark:border-gray-600 font-mono text-lg">
                {{ telegramId }}
              </code>
              <button
                @click="copyTelegramId"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <svg v-if="!copied" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{{ copied ? 'Скопировано!' : 'Копировать' }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Для заблокированных пользователей -->
        <div v-else-if="reason === 'blocked'" class="space-y-4">
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
              Ваш аккаунт был заблокирован. Для получения дополнительной информации обратитесь к администратору вашей организации.
            </p>
          </div>
        </div>

        <!-- Для пользователей без организации -->
        <div v-else-if="reason === 'no_organization'" class="space-y-4">
          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
            <p class="text-sm text-orange-800 dark:text-orange-200">
              Ваш аккаунт не привязан к организации. Обратитесь к администратору для завершения настройки.
            </p>
          </div>
        </div>

        <!-- Кнопки действий -->
        <div class="flex gap-3 mt-6">
          <button
            @click="checkAccessAgain"
            :disabled="checking"
            class="flex-1 px-4 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
          >
            <svg v-if="!checking" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ checking ? 'Проверка...' : 'Проверить снова' }}</span>
          </button>

          <button
            @click="contactSupport"
            class="px-4 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors font-medium"
          >
            Поддержка
          </button>
        </div>
      </div>

      <!-- Дополнительная информация -->
      <div class="text-center text-sm text-gray-500 dark:text-gray-400">
        <p>Это закрытая B2B система</p>
        <p>Доступ предоставляется только администраторами</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  reason: {
    type: String,
    required: true
  },
  telegramId: {
    type: [Number, String],
    default: null
  }
})

const authStore = useAuthStore()
const copied = ref(false)
const checking = ref(false)

const copyTelegramId = async () => {
  try {
    await navigator.clipboard.writeText(String(props.telegramId))
    copied.value = true
    
    // Вибрация при копировании
    telegramService.vibrate('success')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Copy failed:', err)
    telegramService.showAlert('Не удалось скопировать ID')
  }
}

const checkAccessAgain = async () => {
  checking.value = true
  try {
    await authStore.checkAccess()
    
    if (authStore.hasAccess) {
      // Если доступ появился - пытаемся войти
      const result = await authStore.login()
      if (result.success) {
        // Успешный вход - перезагружаем страницу
        window.location.reload()
      }
    } else {
      telegramService.showAlert('Доступ пока не предоставлен')
    }
  } catch (err) {
    console.error('Check access error:', err)
    telegramService.showAlert('Ошибка при проверке доступа')
  } finally {
    checking.value = false
  }
}

const contactSupport = () => {
  // Можно открыть чат поддержки в Telegram
  telegramService.showAlert('Свяжитесь с администратором вашей организации для получения доступа')
}
</script>