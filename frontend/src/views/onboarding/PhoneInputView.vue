<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 to-indigo-600 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
      <!-- Title -->
      <h1 class="text-2xl font-bold text-gray-900 mb-2 text-center">
        Укажите номер телефона
      </h1>
      
      <p class="text-gray-600 mb-6 text-center text-sm">
        Номер телефона нужен для обратной связи оператора или курьера
      </p>

      <!-- Error message -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <!-- Waiting for contact message -->
      <div v-if="waitingForContact" class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-4 text-sm text-center">
        <div class="flex items-center justify-center gap-2">
          <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Ожидание получения номера телефона...</span>
        </div>
      </div>

      <!-- Phone input -->
      <div class="space-y-4">
        <!-- Telegram requestContact button (only in Telegram) -->
        <div v-if="isInTelegram && !phone && !waitingForContact">
          <button
            @click="requestContact"
            :disabled="waitingForContact"
            class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2 mb-4"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span>Поделиться номером телефона</span>
          </button>
          <div class="text-center mb-4">
            <span class="text-gray-500 text-sm">или</span>
          </div>
        </div>

        <!-- Manual input -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Номер телефона <span class="text-red-500">*</span>
          </label>
          <input
            v-model="phone"
            type="tel"
            required
            placeholder="+7 (700) 123 45 67"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
            @input="formatPhone"
          />
          <p class="text-xs text-gray-500 mt-1">
            Формат: +7 (700) 123 45 67
          </p>
        </div>

        <!-- Continue button -->
        <button
          @click="handleContinue"
          :disabled="saving || !phone"
          class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2"
        >
          <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ saving ? 'Сохранение...' : 'Продолжить' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import usersService from '@/services/users.service'

const router = useRouter()
const authStore = useAuthStore()

const phone = ref('')
const saving = ref(false)
const error = ref('')
const isInTelegram = ref(false)
const waitingForContact = ref(false)
let mainButtonClickHandler = null
let autoContinueTriggered = false
let contactRequestedEventHandler = null
let retryTimeout = null

/**
 * Запросить телефон из базы данных
 * Простой запрос без polling
 */
async function fetchPhoneFromBackend() {
  try {
    await authStore.fetchCurrentUser()
    return authStore.user?.phone || ''
  } catch (e) {
    // игнорируем — может быть временная сеть/401
    return ''
  }
}

function normalizePhoneValue(value) {
  const raw = String(value || '').replace(/[^\d+]/g, '')
  const digits = raw.replace(/\D/g, '')

  if (!digits) return ''
  if (digits.startsWith('7')) return `+${digits}`
  if (digits.startsWith('8')) return `+7${digits.slice(1)}`
  return `+7${digits}`
}

/**
 * Попытка получить телефон из базы после запроса контакта
 * Делаем одну попытку через 3 секунды (время на сохранение в базу)
 */
async function tryFetchPhoneAfterContact() {
  // Очищаем предыдущий таймаут если есть
  if (retryTimeout) {
    clearTimeout(retryTimeout)
    retryTimeout = null
  }

  // Ждем 3 секунды, чтобы сторонний инструмент успел сохранить телефон в базу
  retryTimeout = setTimeout(async () => {
    // Не перетираем ручной ввод
    if (phone.value) {
      return
    }

    const phoneFromBackend = await fetchPhoneFromBackend()
    if (phoneFromBackend) {
      phone.value = normalizePhoneValue(phoneFromBackend)
      error.value = ''
      waitingForContact.value = false
      
      // Автоматически продолжаем если телефон получен
      if (!autoContinueTriggered && !saving.value) {
        autoContinueTriggered = true
        setTimeout(() => {
          handleContinue()
        }, 500)
      }
    }
    retryTimeout = null
  }, 3000)
}

onMounted(async () => {
  isInTelegram.value = telegramService.isInTelegram()
  
  // При загрузке компонента проверяем, есть ли уже телефон в базе
  const phoneFromBackend = await fetchPhoneFromBackend()
  if (phoneFromBackend) {
    phone.value = normalizePhoneValue(phoneFromBackend)
  }
})

onUnmounted(() => {
  // Очистка при размонтировании
  if (retryTimeout) {
    clearTimeout(retryTimeout)
    retryTimeout = null
  }
  
  if (isInTelegram.value && contactRequestedEventHandler) {
    const webApp = window.Telegram?.WebApp
    if (webApp?.offEvent) {
      webApp.offEvent('contactRequested', contactRequestedEventHandler)
    }
    contactRequestedEventHandler = null
  }
  if (isInTelegram.value && mainButtonClickHandler) {
    const webApp = window.Telegram?.WebApp
    if (webApp?.MainButton) {
      webApp.MainButton.offClick(mainButtonClickHandler)
      webApp.MainButton.hide()
    }
  }
})

// Следим за изменением телефона и скрываем MainButton если телефон введен
watch(phone, (newPhone) => {
  if (newPhone && isInTelegram.value) {
    // Если пользователь начал вводить телефон вручную — прекращаем ожидание контакта
    if (waitingForContact.value) {
      waitingForContact.value = false
      if (retryTimeout) {
        clearTimeout(retryTimeout)
        retryTimeout = null
      }
    }
    const webApp = window.Telegram?.WebApp
    if (webApp?.MainButton && mainButtonClickHandler) {
      webApp.MainButton.hide()
      webApp.MainButton.offClick(mainButtonClickHandler)
      mainButtonClickHandler = null
    }
  }
})

async function requestContact() {
  if (!isInTelegram.value) return
  
  const webApp = window.Telegram?.WebApp
  if (!webApp) return
  
  error.value = ''
  autoContinueTriggered = false

  const finishSuccess = (phoneFromBackend) => {
    const normalized = normalizePhoneValue(phoneFromBackend)
    if (!normalized) return false
    waitingForContact.value = false
    phone.value = normalized

    if (!autoContinueTriggered && !saving.value) {
      autoContinueTriggered = true
      setTimeout(() => {
        handleContinue()
      }, 500)
    }
    return true
  }

  const finishManual = (message) => {
    waitingForContact.value = false
    error.value = message
    // Делаем одну попытку получить телефон через 3 секунды
    // (время на сохранение в базу сторонним инструментом)
    tryFetchPhoneAfterContact()
  }

  // Современный путь: Telegram WebApp.requestContact()
  if (typeof webApp.requestContact === 'function') {
    waitingForContact.value = true

    // Один раз слушаем статус (sent/cancelled) и, если sent, подтягиваем телефон с бекенда
    if (contactRequestedEventHandler) {
      webApp.offEvent?.('contactRequested', contactRequestedEventHandler)
      contactRequestedEventHandler = null
    }
    contactRequestedEventHandler = async (evt) => {
      const status = evt?.status
      if (status === 'cancelled') {
        finishManual('Вы отменили отправку номера. Введите телефон вручную — он нужен для обратной связи оператора или курьера.')
        return
      }
      if (status === 'sent') {
        // Контакт отправлен, делаем попытку получить телефон через 3 секунды
        tryFetchPhoneAfterContact()
      }
    }
    webApp.onEvent?.('contactRequested', contactRequestedEventHandler)

    try {
      // callback (если поддерживается) сообщает только факт отправки/отмены
      webApp.requestContact((shared) => {
        if (shared === false) {
          finishManual('Вы отменили отправку номера. Введите телефон вручную — он нужен для обратной связи оператора или курьера.')
        }
      })
    } catch (e) {
      // Если метод есть, но упал — даём ручной ввод
      finishManual('Не удалось запросить номер телефона в Telegram. Введите телефон вручную — он нужен для обратной связи оператора или курьера.')
      return
    }

    // Делаем попытку получить телефон через 3 секунды
    // (время на сохранение в базу сторонним инструментом)
    tryFetchPhoneAfterContact()
    return
  }

  // Фоллбек для старых клиентов: просим через MainButton.request_contact
  const mainButton = webApp.MainButton
  if (!mainButton) {
    finishManual('Не удалось запросить номер телефона в Telegram. Введите телефон вручную — он нужен для обратной связи оператора или курьера.')
    return
  }

  mainButton.setText('Поделиться номером')
  mainButton.setParams({ request_contact: true })
  mainButton.show()

  mainButtonClickHandler = async () => {
    waitingForContact.value = true
    error.value = ''

    // Делаем попытку получить телефон через 3 секунды
    // (время на сохранение в базу сторонним инструментом)
    tryFetchPhoneAfterContact()
    
    // Скрываем кнопку, так как контакт уже запрошен
    mainButton.hide()
    mainButton.offClick(mainButtonClickHandler)
    mainButtonClickHandler = null
  }

  mainButton.onClick(mainButtonClickHandler)
}

function formatPhone(event) {
  // Простая валидация формата телефона
  let value = event.target.value.replace(/\D/g, '')
  if (value.startsWith('7')) {
    value = '+' + value
  } else if (value.startsWith('8')) {
    value = '+7' + value.slice(1)
  } else if (!value.startsWith('+')) {
    value = '+7' + value
  }
  phone.value = value
}

async function handleContinue() {
  if (!phone.value) {
    error.value = 'Пожалуйста, укажите номер телефона'
    return
  }

  // Валидация формата
  const cleanPhone = phone.value.replace(/\D/g, '')
  if (cleanPhone.length !== 11 || !cleanPhone.startsWith('7')) {
    error.value = 'Введите корректный номер телефона (например: +77001234567)'
    return
  }

  saving.value = true
  error.value = ''

  try {
    // Сохраняем телефон через API
    await usersService.updateProfile({ phone: phone.value })
    
    // Обновляем данные пользователя в store
    await authStore.fetchCurrentUser()
    
    // Переходим к вводу адреса
    router.push('/onboarding/address')
  } catch (err) {
    console.error('Save phone error:', err)
    error.value = err.response?.data?.phone?.[0] || 'Не удалось сохранить номер телефона. Попробуйте еще раз.'
  } finally {
    saving.value = false
  }
}
</script>
