<script setup>
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import authService from '@/services/auth.service'
import BottomNav from '@/components/common/BottomNav.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Скрывать навигацию на странице логина, в админке, onboarding и для админов в десктопе
const showBottomNav = computed(() => {
  // Если не в Telegram и пользователь админ - не показываем BottomNav
  const isAdmin = authStore.isAuthenticated && 
    (authStore.user?.role_name === 'superadmin' || authStore.user?.role_name === 'org_admin')
  const isDesktop = !telegramService.isInTelegram()
  
  if (isDesktop && isAdmin) {
    return false
  }
  
  return route.name !== 'login' && 
         !route.path.startsWith('/admin') && 
         !route.path.startsWith('/onboarding') &&
         route.name !== 'access-denied'
})

onMounted(async () => {
  try {
    // Инициализация Telegram
    telegramService.init()
    
    // Дополнительная проверка окружения для отладки
    const isInTelegram = telegramService.isInTelegram()
    console.log('[App] Environment check:', {
      isInTelegram,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'N/A',
      hasWebApp: !!telegramService.webApp,
      initData: telegramService.webApp?.initData ? 'present' : 'missing',
      platform: telegramService.webApp?.platform,
      hasUser: !!telegramService.webApp?.initDataUnsafe?.user
    })
    
    // Если запущено в Telegram
    if (isInTelegram) {
      const tgUser = telegramService.getUser()
      if (tgUser) {
        console.log('TG User:', tgUser.id)
        
        // B2C: максимально быстрый старт:
        // 1) если уже есть access_token — сначала пробуем просто подтянуть /users/me/
        // 2) если токена нет/он протух — делаем Telegram login (1 запрос)
        if (authService.isAuthenticated() && !authStore.isAuthenticated) {
          await authStore.fetchCurrentUser()
        }

        let loginResult = { success: true }
        if (!authStore.isAuthenticated) {
          loginResult = await authStore.login()
        }

        if (!loginResult.success) {
            console.error('Login failed:', loginResult.message)
            // Если ошибка - показываем страницу доступа (на случай если пользователь заблокирован)
            if (loginResult.error?.includes('заблокирован') || loginResult.error?.includes('blocked')) {
                router.push({ 
                    name: 'access-denied', 
                    query: { id: tgUser.id } 
                })
            }
        } else {
            // Проверяем наличие телефона и адреса
            if (authStore.isAuthenticated) {
                const user = authStore.user
                console.log('User after login:', user)
                console.log('User phone:', user?.phone)
                console.log('User addresses:', user?.addresses)
                
                // Если нет телефона - редирект на welcome (первый экран onboarding)
                if (!user?.phone) {
                    console.log('User has no phone, redirecting to welcome')
                    router.push('/onboarding/welcome')
                    return
                }
                // Если нет адреса доставки - редирект на ввод адреса
                if (!user?.addresses || user.addresses.length === 0) {
                    console.log('User has no address, redirecting to address input')
                    router.push('/onboarding/address')
                    return
                }
                // Если нет терминалов - редирект на выбор терминала
                if (!user?.terminals || user.terminals.length === 0) {
                    console.log('User has no terminals, redirecting to terminal selection')
                    router.push('/onboarding/terminal')
                    return
                }
            }
        }
      }
    } else {
        // Если запущено в браузере (десктоп)
        console.log('[App] Desktop mode detected')
        // Проверяем, есть ли токен в localStorage
        if (authService.isAuthenticated()) {
            // Если токен есть, но пользователь не загружен - загружаем
            if (!authStore.isAuthenticated) {
                console.log('[App] Loading user from token...')
                await authStore.fetchCurrentUser()
            }
            
            // Если авторизован
            if (authStore.isAuthenticated) {
                const user = authStore.user
                console.log('[App] Desktop user loaded:', user)
                const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
                console.log('[App] Desktop isAdmin:', isAdmin, 'route:', route.name, 'path:', route.path)
                
                // Если на странице логина - редирект в зависимости от роли
                if (route.name === 'login') {
                    if (isAdmin) {
                        console.log('[App] Desktop: redirecting from login to /admin')
                        router.push('/admin')
                        return
                    } else {
                        console.log('[App] Desktop: redirecting from login to /')
                        router.push('/')
                        return
                    }
                }
                // Если на главной странице и админ - редирект в админку
                if ((route.name === 'home' || route.path === '/') && isAdmin) {
                    console.log('[App] Desktop: redirecting from home to /admin')
                    router.push('/admin')
                    return
                }
            }
        } else {
            // Если нет токена и не на странице логина - редирект на логин
            if (route.name !== 'login' && route.name !== 'access-denied') {
                console.log('[App] Desktop: no token, redirecting to /login')
                router.push('/login')
            }
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