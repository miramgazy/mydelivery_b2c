<script setup>
import { ref, onMounted, computed, watch, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import Navigation from '@/components/Navigation.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const router = useRouter()
const authStore = useAuthStore()

const isCheckingAccess = ref(true)
const telegramId = ref(null)

// Глобальный перехватчик ошибок для Telegram
window.onerror = function(message, source, lineno, colno, error) {
  alert(`JS ERROR: ${message}\nSource: ${source}\nLine: ${lineno}`);
};

const isAdminPath = computed(() => router.currentRoute.value.path.startsWith('/admin'))

onMounted(async () => {
  alert('ВЕРСИЯ 1.0.6: Старт...')
  
  try {
    // 1. Инициализируем Telegram
    alert('Шаг 1: TG Init...')
    telegramService.init()
    
    if (!telegramService.isInTelegram()) {
      alert('Внимание: Запущено не в Telegram');
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    telegramId.value = tgUser?.id
    alert(`Шаг 2: ID получен: ${telegramId.value}`)

    // 2. Проверяем доступ через Store
    alert('Шаг 3: Вызываю checkAccess...')
    
    // Делаем таймаут на случай зависания запроса
    const timeout = setTimeout(() => {
      alert('ВНИМАНИЕ: Запрос checkAccess длится более 10 секунд!')
    }, 10000);

    const result = await authStore.checkAccess()
    clearTimeout(timeout);
    
    alert(`Шаг 4: Ответ API: ${JSON.stringify(result)}`)

    if (!authStore.hasAccess) {
      alert('Доступ запрещен бэкендом');
      isCheckingAccess.value = false
      return
    }

    // 3. Доступ есть - входим
    alert('Шаг 5: Вызываю Login...')
    const loginResult = await authStore.login()
    alert(`Шаг 6: Результат Login: ${JSON.stringify(loginResult)}`)
    
    if (loginResult.success) {
      await authStore.fetchCurrentUser()
      router.push('/')
    }

  } catch (err) {
    alert(`КРИТИЧЕСКАЯ ОШИБКА: ${err.message}\nStack: ${err.stack}`)
    console.error('Initial error:', err)
  } finally {
    isCheckingAccess.value = false
  }
})
</script>

<template>
  <div class="app-container">
    <router-view v-if="!isCheckingAccess"></router-view>
    <div v-else class="checking-screen">
      <div class="loader"></div>
      <p>Проверка доступа [v1.0.6]...</p>
    </div>
    
    <!-- Навигация только для основых путей (не админка и не проверка) -->
    <Navigation v-if="!isCheckingAccess && !isAdminPath" />
  </div>
</template>

<style>
.checking-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #111;
  color: white;
}
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>