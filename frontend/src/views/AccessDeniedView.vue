<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-8 text-center">
      <!-- Icon -->
      <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>

      <!-- Title -->
      <h1 class="text-2xl font-bold text-gray-900 mb-2">
        Доступ ограничен
      </h1>
      
      <!-- Description -->
      <p class="text-gray-600 mb-6">
        Ваш аккаунт был заблокирован или временно недоступен.
      </p>

      <p class="text-gray-600 text-sm mb-6">
        Если вы считаете, что это ошибка, пожалуйста, свяжитесь с поддержкой.
      </p>

      <!-- ID Display -->
      <div class="bg-gray-100 rounded-xl p-4 mb-6 relative group cursor-pointer" @click="copyId">
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Ваш Telegram ID</p>
        <p class="text-xl font-mono font-bold text-gray-800">{{ telegramId || 'Не определен' }}</p>
        
        <div class="absolute right-3 top-1/2 -translate-y-1/2 opacity-50 group-hover:opacity-100 transition-opacity">
            <svg class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
        </div>
      </div>

      <!-- Button -->
      <button 
        @click="copyId"
        class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2"
      >
        <span>{{ copied ? 'Скопировано!' : 'Скопировать ID' }}</span>
      </button>

      <div class="mt-8 text-xs text-gray-400">
        B2C Delivery System
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import telegramService from '@/services/telegram'

const telegramId = ref('')
const copied = ref(false)

onMounted(() => {
    // Пытаемся получить ID из Telegram InitData
    if (telegramService.isInTelegram()) {
        const user = telegramService.getUser()
        if (user) {
            telegramId.value = user.id
        }
    }
    
    // Если передан через query (для надежности)
    const urlParams = new URLSearchParams(window.location.search);
    const idFromUrl = urlParams.get('id');
    if (idFromUrl) {
        telegramId.value = idFromUrl;
    }
})

const copyId = async () => {
    if (!telegramId.value) return;
    
    try {
        await navigator.clipboard.writeText(telegramId.value.toString());
        copied.value = true;
        
        // Вибрация
        telegramService.vibrate('light');
        
        setTimeout(() => {
            copied.value = false;
        }, 2000);
    } catch (err) {
        console.error('Failed to copy', err);
    }
}
</script>
