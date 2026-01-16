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
  await startApp();
})

async function startApp() {
  try {
    isCheckingAccess.value = true;
    errorState.value = false;
    
    // 1. Инициализация Telegram с задержкой (Разогрев WebView)
    statusMessage.value = 'Подключение к Telegram...';
    await new Promise(resolve => setTimeout(resolve, 500)); 
    
    console.log('Initializing telegram service...');
    telegramService.init()
    
    console.log('Checking if in Telegram...');
    if (!telegramService.isInTelegram()) {
      console.warn('NOT IN TELEGRAM (initData missing)');
      isCheckingAccess.value = false
      return
    }

    const tgUser = telegramService.getUser()
    console.log('Telegram user data:', tgUser);
    
    if (!tgUser) {
        throw new Error('Данные пользователя Telegram не получены');
    }
    
    // 2. Проверка доступа
    statusMessage.value = `ID: ${tgUser.id}. Синхронизация...`;
    
    // Запускаем запрос
    const result = await authStore.checkAccess();
    
    if (result && result.has_access) {
        statusMessage.value = 'Вход в систему...';
        const logRes = await authStore.login();
        
        if (logRes.success) {
            statusMessage.value = 'Готово!';
            router.push('/');
            isCheckingAccess.value = false;
        } else {
            throw new Error(logRes.message || 'Ошибка входа');
        }
    } else {
        throw new Error(result?.message || 'Доступ запрещен');
    }

  } catch (err) {
    console.error('INIT ERROR:', err);
    statusMessage.value = err.message;
    errorState.value = true;
    isCheckingAccess.value = true; // Оставляем экран загрузки, но с кнопкой
  }
}

const errorState = ref(false);

function retry() {
    startApp();
}

</script>

<template>
  <div class="app-container">
    <router-view v-if="!isCheckingAccess"></router-view>
    <div v-else class="checking-screen">
      <div class="matrix-loader"></div>
      <p class="matrix-text">{{ statusMessage }}</p>
      
      <button v-if="errorState" @click="retry" class="retry-btn">
        ПОВТОРИТЬ ПОПЫТКУ
      </button>

      <div style="font-size: 8px; color: #555; margin-top: 50px;">DEBUG VERSION 1.3.1 - RETRY FIX</div>
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

.retry-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #0f0;
  color: #0f0;
  font-family: monospace;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #0f0;
  color: #000;
  box-shadow: 0 0 10px #0f0;
}

</style>