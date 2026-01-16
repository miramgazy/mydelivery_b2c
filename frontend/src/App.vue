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
    // Инициализация Telegram
    telegramService.init()
    
    // Если запущено в Telegram
    if (telegramService.isInTelegram()) {
      const tgUser = telegramService.getUser()
      if (tgUser) {
        console.log('TG User:', tgUser.id)
        
        // Всегда проверяем доступ при старте, чтобы обновить токены
        const accessCheck = await authStore.checkAccess()
        
        if (accessCheck.has_access) {
            const loginResult = await authStore.login()
            if (!loginResult.success) {
                console.error('Login failed:', loginResult.message)
            }
        } else {
            console.warn('Access denied for user:', tgUser.id)
        }
      }
    } else {
        // Если запущено в браузере и нет токена - редирект на логин
        if (!authStore.isAuthenticated && route.name !== 'login') {
            router.push('/login')
        }
    }
  } catch (err) {
    console.error('App Init Error:', err)
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