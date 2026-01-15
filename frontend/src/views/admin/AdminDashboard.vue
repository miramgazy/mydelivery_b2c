<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
    <h1 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Админ панель</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Quick Stats -->
        <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
            <h3 class="font-bold text-gray-500 mb-2">Заказов сегодня</h3>
            <p class="text-3xl font-bold text-gray-900 dark:text-white">12</p>
        </div>
        
        <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm">
             <h3 class="font-bold text-gray-500 mb-2">Выручка</h3>
             <p class="text-3xl font-bold text-primary-600">45 200 ₸</p>
        </div>

        <!-- Navigation Links -->
        <router-link to="/admin/orders" class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm flex items-center justify-between hover:shadow-md transition-shadow">
            <div class="flex items-center gap-3">
                <div class="p-3 bg-blue-100 text-blue-600 rounded-lg">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                </div>
                <span class="font-bold text-lg text-gray-900 dark:text-white">Управление заказами</span>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
        </router-link>

        <router-link to="/admin/users" class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm flex items-center justify-between hover:shadow-md transition-shadow">
            <div class="flex items-center gap-3">
                <div class="p-3 bg-green-100 text-green-600 rounded-lg">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                </div>
                <span class="font-bold text-lg text-gray-900 dark:text-white">Пользователи</span>
            </div>
             <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
        </router-link>
    </div>
  </div>
</template>

<script setup>
// Admin Dashboard
</script>
