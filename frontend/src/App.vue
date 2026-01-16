<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const router = useRouter()
const authStore = useAuthStore()

const isCheckingAccess = ref(true)
const statusMessage = ref('СИСТЕМА v1.3.0 ЗАГРУЖЕНА...')

onMounted(async () => {
  console.log('--- START ON_MOUNTED ---');
  try {
    console.log('Initializing telegram service...');
    telegramService.init()
    
    console.log('Checking if in Telegram...');
    if (!telegramService.isInTelegram()) {
      console.warn('NOT IN TELEGRAM (initData missing)');
      console.log('WebApp object:', telegramService.webApp);
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    console.log('Telegram user data:', tgUser);
    
    if (!tgUser) {
        console.error('User object is empty/null');
        statusMessage.value = 'ОШИБКА: Данные пользователя Telegram не получены';
        return;
    }
    
    statusMessage.value = `ID: ${tgUser.id}. Проверка доступа...`;
    console.log(`Sending check_access for user ${tgUser.id}...`);

    const response = await fetch('/api/users/check_access/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: tgUser.id })
    });
    
    console.log('Response status:', response.status);

    if (response.ok) {
        const result = await response.json();
        console.log('Access result:', result);
        
        if (result.has_access) {
            statusMessage.value = 'ДОСТУП ЕСТЬ. Авторизация...';
            console.log('Calling authStore.login()...');
            const logRes = await authStore.login();
            console.log('Login result:', logRes);
            
            if (logRes.success) {
                statusMessage.value = 'УСПЕХ. Загрузка приложения...';
                router.push('/');
                isCheckingAccess.value = false;
            } else {
                statusMessage.value = `ОШИБКА ЛОГИНА: ${logRes.message || 'Неизвестная ошибка'}`;
                alert('Ошибка логина: ' + JSON.stringify(logRes));
            }
        } else {
            console.warn('Access denied by backend');
            statusMessage.value = `ОТКАЗАНО: ${result.message || 'Доступ запрещен'}`;
        }
    } else {
        const errText = await response.text();
        console.error('API Error text:', errText);
        statusMessage.value = `ОШИБКА API: ${response.status}`;
        alert(`API Error (${response.status}): ${errText}`);
    }

  } catch (err) {
    console.error('FATAL ERROR:', err);
    statusMessage.value = `КРИТИЧЕСКАЯ ОШИБКА: ${err.message}`;
    alert('Fatal Error: ' + err.stack);
  }
})
</script>

<template>
  <div class="app-container">
    <router-view v-if="!isCheckingAccess"></router-view>
    <div v-else class="checking-screen">
      <div class="matrix-loader"></div>
      <p class="matrix-text">{{ statusMessage }}</p>
      <div style="font-size: 8px; color: #555; margin-top: 50px;">DEBUG VERSION 1.3.0</div>
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
  color: #0f0; /* Зеленый "матричный" текст */
  text-align: center;
  padding: 20px;
  font-family: monospace;
}
.matrix-loader {
  border: 2px solid #030;
  border-top: 2px solid #0f0;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}
.matrix-text {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>