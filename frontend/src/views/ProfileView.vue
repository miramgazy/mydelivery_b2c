<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 flex flex-col items-center border-b border-gray-200 dark:border-gray-700">
        <div class="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-4 text-3xl">
            👋
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ user?.full_name || 'Пользователь' }}</h1>
        <p class="text-gray-500">{{ user?.phone || 'Телефон не указан' }}</p>
    </div>

    <!-- Actions -->
    <div class="p-4 space-y-4">
        <!-- Profile Data -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg">
                Личные данные
            </div>
            <div class="p-4 space-y-4">
                <div>
                     <label class="block text-sm text-gray-500 mb-1">Имя</label>
                     <div class="font-medium">{{ user?.first_name }}</div>
                </div>
                <div>
                     <label class="block text-sm text-gray-500 mb-1">Фамилия</label>
                     <div class="font-medium">{{ user?.last_name || '-' }}</div>
                </div>
                 <div>
                     <label class="block text-sm text-gray-500 mb-1">Telegram ID</label>
                     <div class="font-mono text-sm bg-gray-100 dark:bg-gray-700 p-2 rounded">{{ user?.telegram_id }}</div>
                </div>
            </div>
        </div>

        <!-- Addresses (Placeholder for now) -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
             <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg flex justify-between items-center">
                <span>Мои адреса</span>
                <!-- <button class="text-primary-600 text-sm">Добавить</button> -->
            </div>
            <div class="p-4 text-center text-gray-500 text-sm italic">
                Адреса сохраняются автоматически при заказе
            </div>
        </div>

         <!-- About -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
             <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg">
                О приложении
            </div>
            <div class="p-4 space-y-2">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Версия</span>
                    <span>1.0.0</span>
                </div>
                 <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Организация</span>
                    <span>{{ user?.organization_name || '-' }}</span>
                </div>
            </div>
        </div>
        
        <!-- Logout -->
        <button 
            @click="logout"
            class="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
            Выйти
        </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const user = computed(() => authStore.user)

const logout = () => {
    telegramService.showConfirm('Вы уверены, что хотите выйти?', () => {
        authStore.logout()
        router.push('/')
        notificationStore.show('Вы вышли из системы')
    })
}
</script>
