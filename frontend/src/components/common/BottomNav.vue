<template>
  <nav class="fixed bottom-0 w-full bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg border-t border-gray-200 dark:border-gray-700 py-2 px-6 flex justify-between items-center z-40 pb-safe-bottom">
    <router-link to="/" class="flex flex-col items-center transition-colors px-2" :class="route.path === '/' ? 'text-primary-600' : 'text-gray-400'">
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
      <span class="text-[10px] mt-1 font-medium">Главная</span>
    </router-link>
    
    <router-link to="/menu" class="flex flex-col items-center transition-colors px-2" :class="route.path === '/menu' ? 'text-primary-600' : 'text-gray-400'">
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <span class="text-[10px] mt-1 font-medium">Меню</span>
    </router-link>
    
    <router-link to="/orders" class="flex flex-col items-center transition-colors px-2" :class="route.path.startsWith('/orders') ? 'text-primary-600' : 'text-gray-400'">
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
      <span class="text-[10px] mt-1 font-medium">Заказы</span>
    </router-link>
    
    <router-link to="/profile" class="flex flex-col items-center transition-colors px-2" :class="route.path === '/profile' ? 'text-primary-600' : 'text-gray-400'">
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
      <span class="text-[10px] mt-1 font-medium">Профиль</span>
    </router-link>

    <button @click="closeApp" class="flex flex-col items-center text-gray-400 hover:text-red-500 transition-colors px-2">
      <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
      <span class="text-[10px] mt-1 font-medium">Закрыть</span>
    </button>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import telegramService from '@/services/telegram'

const route = useRoute()

const closeApp = () => {
  telegramService.close()
}
</script>

<style scoped>
.pb-safe-bottom {
  padding-bottom: calc(0.5rem + env(safe-area-inset-bottom));
}
</style>
