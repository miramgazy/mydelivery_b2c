<template>
  <div class="min-h-screen bg-[#0f172a] flex items-center justify-center p-4 relative overflow-hidden font-sans">
    <!-- Background decorative blobs -->
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/20 rounded-full blur-[120px] animate-pulse"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px] animate-pulse" style="animation-delay: 2s"></div>
    
    <div class="w-full max-w-[440px] z-10">
      <!-- Logo/Brand Area -->
      <div class="text-center mb-10 transition-all duration-700 animate-in fade-in slide-in-from-bottom-4">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-tr from-primary-600 to-indigo-500 shadow-2xl shadow-primary-500/30 mb-6 group hover:rotate-6 transition-transform">
          <svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </div>
        <h2 class="text-4xl font-extrabold text-white tracking-tight mb-2">
          TG Delivery
        </h2>
        <p class="text-slate-400 text-lg font-medium">
          Панель управления
        </p>
      </div>

      <!-- Glass Card -->
      <div class="bg-slate-800/40 backdrop-blur-2xl border border-white/10 rounded-[32px] p-8 md:p-10 shadow-2xl animate-in zoom-in-95 duration-500">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div class="space-y-2">
            <label for="username" class="block text-sm font-semibold text-slate-300 ml-1">
              Логин
            </label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none group-focus-within:text-primary-400 text-slate-500 transition-colors">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="block w-full pl-12 pr-4 py-4 bg-slate-900/50 border border-white/5 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all border-none shadow-inner"
                placeholder="admin"
              />
            </div>
          </div>

          <div class="space-y-2">
            <label for="password" class="block text-sm font-semibold text-slate-300 ml-1">
              Пароль
            </label>
            <div class="relative group">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none group-focus-within:text-primary-400 text-slate-500 transition-colors">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                class="block w-full pl-12 pr-4 py-4 bg-slate-900/50 border border-white/5 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all border-none shadow-inner"
                placeholder="••••••••"
              />
            </div>
          </div>

          <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl text-sm font-medium animate-pulse">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex items-center justify-center py-4 px-6 rounded-2xl text-lg font-bold text-white bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-800 transition-all active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100 overflow-hidden shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)]"
          >
            <!-- Animated overlay -->
            <div class="absolute inset-0 bg-white/10 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500"></div>
            
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span class="relative z-10">{{ loading ? 'Авторизация...' : 'Войти в систему' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer Info -->
      <p class="mt-8 text-center text-slate-500 text-sm font-medium uppercase tracking-widest">
        &copy; 2024 TG Delivery System
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.loginWithPassword(form.username, form.password)
    if (result.success) {
      // Ждем обновления данных пользователя
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Проверяем роль пользователя
      const user = authStore.user
      console.log('User after login:', user)
      console.log('User role_name:', user?.role_name)
      
      const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
      console.log('Is admin:', isAdmin)
      
      if (isAdmin) {
        console.log('Redirecting to /admin')
        router.push('/admin')
      } else {
        console.log('Redirecting to /')
        router.push('/')
      }
    } else {
      error.value = result.error || 'Неверный логин или пароль'
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'Ошибка подключения к серверу'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Keyframes for animations */
@keyframes in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: in 0.6s ease-out forwards;
}

/* Custom shadow inner for inputs */
.shadow-inner {
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.2);
}
</style>
