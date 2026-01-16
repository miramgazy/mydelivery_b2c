<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const router = useRouter()
const authStore = useAuthStore()

const isCheckingAccess = ref(true)
const statusMessage = ref('ЗАПУСК КОДА v1.2.0...')

onMounted(async () => {
  try {
    telegramService.init()
    if (!telegramService.isInTelegram()) {
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    statusMessage.value = `ID: ${tgUser?.id}. Проверка...`

    // Прямой вызов fetch без посредников
    const response = await fetch('/api/users/check_access/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: tgUser.id })
    });
    
    statusMessage.value = `Response: ${response.status}`;
    
    if (response.ok) {
        const result = await response.json();
        if (result.has_access) {
            statusMessage.value = 'Доступ есть! Вхожу...';
            const logRes = await authStore.login();
            if (logRes.success) {
                router.push('/');
                isCheckingAccess.value = false;
            }
        } else {
            statusMessage.value = 'Доступ запрещен в БД';
        }
    } else {
        statusMessage.value = `Ошибка API: ${response.status}`;
    }

  } catch (err) {
    statusMessage.value = `ERROR: ${err.message}`;
  }
})
</script>

<template>
  <div class="app-container">
    <router-view v-if="!isCheckingAccess"></router-view>
    <div v-else class="checking-screen">
      <div class="loader"></div>
      <p style="font-weight: bold;">{{ statusMessage }}</p>
      <div style="font-size: 10px; margin-top: 20px;">Если вы видите этот текст, значит кэш сброшен (v1.2.0)</div>
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
  background: #900; /* Темно-красный фон для отличия версии */
  color: white;
  text-align: center;
  padding: 20px;
}
.loader {
  border: 4px solid rgba(255,255,255,0.1);
  border-top: 4px solid #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>