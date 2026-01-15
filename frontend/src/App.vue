<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const router = useRouter()
const authStore = useAuthStore()

const isCheckingAccess = ref(true)
const statusMessage = ref('Инициализация v1.1.0...')

onMounted(async () => {
  try {
    statusMessage.value = 'Шаг 1: Telegram init...'
    telegramService.init()
    
    if (!telegramService.isInTelegram()) {
      statusMessage.value = 'Запущено вне Telegram'
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    statusMessage.value = `Шаг 2: ID ${tgUser?.id}. Запрос доступа...`

    // Проверяем доступ
    const result = await authStore.checkAccess()
    statusMessage.value = `Шаг 3: Ответ сервера: hasAccess=${result.has_access}`

    if (!result.has_access) {
      statusMessage.value = 'Доступ запрещен'
      isCheckingAccess.value = false
      return
    }

    // Входим
    statusMessage.value = 'Шаг 4: Авторизация...'
    const loginResult = await authStore.login()
    
    if (loginResult.success) {
      statusMessage.value = 'Успех! Переход в приложение...'
      await authStore.fetchCurrentUser()
      router.push('/')
    } else {
      statusMessage.value = `Ошибка входа: ${loginResult.message}`
    }

  } catch (err) {
    statusMessage.value = `ОШИБКА: ${err.message}`
  } finally {
    // Не снимаем экран загрузки, если была ошибка, чтобы прочитать её
    if (statusMessage.value.includes('Успех') || !telegramService.isInTelegram()) {
       isCheckingAccess.value = false
    }
  }
})
</script>

<template>
  <div class="app-container">
    <router-view v-if="!isCheckingAccess"></router-view>
    <div v-else class="checking-screen">
      <div class="loader"></div>
      <p>{{ statusMessage }}</p>
      <button @click="isCheckingAccess = false" style="margin-top: 20px; font-size: 10px; opacity: 0.5;">[Пропустить]</button>
    </div>
  </div>
</template>

<style>
.checking-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #000;
  color: #3498db;
  font-family: sans-serif;
  text-align: center;
  padding: 20px;
}
.loader {
  border: 4px solid #111;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>