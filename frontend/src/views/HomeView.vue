<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-primary-600 pt-8 pb-16 px-4 rounded-b-3xl relative overflow-hidden">
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
        
        <div class="relative z-10">
            <h1 class="text-2xl font-bold text-white mb-1">
                Добро пожаловать,
            </h1>
            <h2 class="text-3xl font-extrabold text-white mb-6">
                {{ user?.first_name || 'Гость' }} 👋
            </h2>
            
            <!-- Quick Actions -->
            <router-link 
                to="/menu"
                class="block w-full bg-white text-primary-600 rounded-xl p-4 shadow-lg active:scale-95 transition-transform flex items-center justify-between group"
            >
                <div class="flex items-center gap-4">
                    <div class="p-3 bg-primary-100 rounded-full">
                        <svg class="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                    </div>
                    <div class="text-left">
                        <p class="font-bold text-lg">Сделать заказ</p>
                        <p class="text-sm text-gray-500">Вкусная еда ждет вас</p>
                    </div>
                </div>
                <svg class="w-6 h-6 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </router-link>
        </div>
    </div>

    <!-- Active Orders Preview -->
    <div class="px-4 -mt-8 relative z-10" v-if="activeOrder">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border-l-4 border-yellow-400">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-gray-900 dark:text-white">Активный заказ</h3>
                <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">{{ activeOrder.status_display }}</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                Заказ #{{ activeOrder.order_number }}
            </p>
            <router-link 
                :to="'/orders/' + activeOrder.order_id"
                class="text-primary-600 text-sm font-semibold hover:underline"
            >
                Отследить статус →
            </router-link>
        </div>
    </div>

    <!-- Features Grid -->
    <div class="p-4 grid grid-cols-2 gap-4 mt-2">
        <router-link to="/orders" class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mb-3">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
            </div>
            <h3 class="font-bold text-gray-900 dark:text-white">Мои заказы</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">История покупок</p>
        </router-link>

        <router-link to="/profile" class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-3">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
            </div>
            <h3 class="font-bold text-gray-900 dark:text-white">Профиль</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">Ваши данные</p>
        </router-link>
        
        <div v-if="isAdmin" class="col-span-2">
             <router-link to="/admin" class="flex items-center gap-4 bg-gray-900 dark:bg-gray-700 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow text-white">
                <div class="w-10 h-10 bg-gray-700 dark:bg-gray-600 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </div>
                <div>
                    <h3 class="font-bold">Админ панель</h3>
                    <p class="text-xs text-gray-400">Управление рестораном</p>
                </div>
             </router-link>
        </div>
    </div>
    
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useOrdersStore } from '@/stores/orders'

const authStore = useAuthStore()
const ordersStore = useOrdersStore()

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isSuperAdmin || authStore.isOrgAdmin)
const activeOrder = computed(() => ordersStore.activeOrders[0])

onMounted(() => {
    // Refresh orders to check active one
    ordersStore.fetchMyOrders().catch(console.error)
})
</script>

<style scoped>
.pb-safe-bottom {
    padding-bottom: calc(0.5rem + env(safe-area-inset-bottom));
}
</style>
