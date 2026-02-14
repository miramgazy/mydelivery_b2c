<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700',
        'transition-all duration-300 ease-in-out',
        sidebarOpen ? 'w-64' : 'w-16'
      ]"
    >
      <!-- Toggle Button -->
      <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        <h1 
          v-if="sidebarOpen" 
          class="text-xl font-bold text-gray-900 dark:text-white truncate"
        >
          Admin Panel
        </h1>
        <button
          @click="toggleSidebar"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <Icon 
            :icon="sidebarOpen ? 'mdi:menu-open' : 'mdi:menu'" 
            class="w-6 h-6 text-gray-600 dark:text-gray-300"
          />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="p-4 space-y-2 overflow-y-auto h-[calc(100vh-4rem)]">
        <!-- Organization Section -->
        <div class="mb-6">
          <div 
            class="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
            :class="{ 'justify-center': !sidebarOpen }"
          >
            <Icon icon="mdi:office-building" class="w-4 h-4" />
            <span v-if="sidebarOpen">Организация</span>
          </div>
          <router-link
            to="/admin/organization/settings"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:cog" class="w-5 h-5" />
            <span v-if="sidebarOpen">Настройки</span>
          </router-link>
          <router-link
            to="/admin/organization/terminals"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:tablet" class="w-5 h-5" />
            <span v-if="sidebarOpen">Терминалы</span>
          </router-link>
          <router-link
            to="/admin/organization/stop-list"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:food-off" class="w-5 h-5" />
            <span v-if="sidebarOpen">Стоп-лист</span>
          </router-link>
          <router-link
            to="/admin/organization/payment-types"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:credit-card" class="w-5 h-5" />
            <span v-if="sidebarOpen">Типы оплат</span>
          </router-link>
          <router-link
            to="/admin/organization/discounts"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:percent" class="w-5 h-5" />
            <span v-if="sidebarOpen">Скидки</span>
          </router-link>
          <router-link
            to="/admin/organization/menu"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:food" class="w-5 h-5" />
            <span v-if="sidebarOpen">Меню</span>
          </router-link>
          <router-link
            to="/admin/organization/delivery-zones"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:map-marker-radius" class="w-5 h-5" />
            <span v-if="sidebarOpen">Зоны доставки</span>
          </router-link>
        </div>

        <!-- Orders Section -->
        <div class="mb-6">
          <div 
            class="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
            :class="{ 'justify-center': !sidebarOpen }"
          >
            <Icon icon="mdi:shopping" class="w-4 h-4" />
            <span v-if="sidebarOpen">Заказы</span>
          </div>
          <router-link
            to="/admin/orders"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:clipboard-list" class="w-5 h-5" />
            <span v-if="sidebarOpen">Все заказы</span>
          </router-link>
        </div>

        <!-- Clients Section -->
        <div class="mb-6">
          <div 
            class="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
            :class="{ 'justify-center': !sidebarOpen }"
          >
            <Icon icon="mdi:account-group" class="w-4 h-4" />
            <span v-if="sidebarOpen">Клиенты</span>
          </div>
          <router-link
            to="/admin/users"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:account-multiple" class="w-5 h-5" />
            <span v-if="sidebarOpen">Пользователи</span>
          </router-link>
        </div>

        <!-- Products Section -->
        <div class="mb-6">
          <div 
            class="flex items-center gap-3 px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
            :class="{ 'justify-center': !sidebarOpen }"
          >
            <Icon icon="mdi:package-variant" class="w-4 h-4" />
            <span v-if="sidebarOpen">Продукты</span>
          </div>
          <router-link
            to="/admin/products"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:food-variant" class="w-5 h-5" />
            <span v-if="sidebarOpen">Продукты</span>
          </router-link>
          <router-link
            to="/admin/modifiers"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:tune" class="w-5 h-5" />
            <span v-if="sidebarOpen">Модификаторы</span>
          </router-link>
          <router-link
            to="/admin/fast-menu"
            class="nav-item"
            active-class="nav-item-active"
          >
            <Icon icon="mdi:flash" class="w-5 h-5" />
            <span v-if="sidebarOpen">Быстрое меню</span>
          </router-link>
        </div>

        <!-- Logout -->
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            @click="handleLogout"
            class="nav-item w-full text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <Icon icon="mdi:logout" class="w-5 h-5" />
            <span v-if="sidebarOpen">Выход</span>
          </button>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <!-- Header -->
      <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-16 flex items-center justify-between px-6">
        <div class="flex items-center gap-4">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ pageTitle }}
          </h2>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            <Icon icon="mdi:account-circle" class="w-5 h-5 inline mr-2" />
            {{ authStore.user?.username || authStore.user?.first_name }}
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarOpen = ref(true)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const pageTitle = computed(() => {
  const titles = {
    '/admin/organization/settings': 'Настройки организации',
    '/admin/organization/terminals': 'Терминалы',
    '/admin/organization/stop-list': 'Стоп-лист',
    '/admin/organization/payment-types': 'Типы оплат',
    '/admin/organization/discounts': 'Скидки',
    '/admin/organization/menu': 'Управление меню',
    '/admin/organization/delivery-zones': 'Зоны доставки',
    '/admin/orders': 'Заказы',
    '/admin/users': 'Пользователи',
    '/admin/products': 'Продукты',
    '/admin/modifiers': 'Модификаторы',
    '/admin/fast-menu': 'Быстрое меню',
  }
  return titles[route.path] || 'Админ панель'
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-700 dark:text-gray-300 
         hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer;
}

.nav-item-active {
  @apply bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium;
}
</style>
