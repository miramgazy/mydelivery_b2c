<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import Navigation from '@/components/Navigation.vue'

const router = useRouter()
const authStore = useAuthStore()

const isCheckingAccess = ref(true)

// Глобальный перехватчик ошибок
window.onerror = function(message, source, lineno) {
  alert(`JS ERROR: ${message} at ${lineno}`);
};

const isAdminPath = computed(() => router.currentRoute.value.path.startsWith('/admin'))

onMounted(async () => {
  alert('ВЕРСИЯ 1.0.7: Запуск [Чистая сборка]')
  
  try {
    telegramService.init()
    
    if (!telegramService.isInTelegram()) {
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    const telegramId = tgUser?.id
    alert(`Шаг 2: Ваш ID: ${telegramId}`)

    // Проверяем доступ
    await authStore.checkAccess()
    alert(`Шаг 3: Ответ сервера получен. hasAccess=${authStore.hasAccess}`)

    if (!authStore.hasAccess) {
      isCheckingAccess.value = false
      return
    }

    // Входим
    alert('Шаг 4: Начинаю Login...')
    const loginResult = await authStore.login()
    
    if (loginResult.success) {
      await authStore.fetchCurrentUser()
      router.push('/')
    } else {
      alert(`Ошибка Login: ${loginResult.message}`)
    }

  } catch (err) {
    alert(`КРИТИЧЕСКАЯ ОШИБКА: ${err.message}`)
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
      <p>Проверка доступа (v1.0.7)...</p>
    </div>
    
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
  border: 4px solid #333;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>