<script setup>
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import BottomNav from '@/components/common/BottomNav.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Скрывать навигацию на странице логина и в админке
const showBottomNav = computed(() => {
  return route.name !== 'login' && !route.path.startsWith('/admin')
})

onMounted(async () => {
  try {
    // Инициализация Telegram без блокировки интерфейса
    telegramService.init()
    
    // Проверка доступа в фоновом режиме
    if (telegramService.isInTelegram()) {
      const tgUser = telegramService.getUser()
      if (tgUser) {
        console.log('TG User:', tgUser.id)
        if (!authStore.isAuthenticated) {
            await authStore.checkAccess()
            await authStore.login()
        }
      }
    }
  } catch (err) {
    console.warn('Init warning:', err)
  }
})
</script>

<template>
  <div class="app-container">
    <router-view></router-view>
    <BottomNav v-if="showBottomNav" />
    <ToastNotification />
  </div>
</template>

<style>
.app-container {
  width: 100%;
  min-height: 100vh;
  background: var(--tg-theme-bg-color, #fff);
  color: var(--tg-theme-text-color, #000);
}
</style>