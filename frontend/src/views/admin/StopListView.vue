<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Стоп-лист</h2>
      </div>

      <!-- Error Message -->
      <div
        v-if="error"
        class="mx-6 mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
          <Icon icon="mdi:alert-circle" class="w-5 h-5" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading && stopList.length === 0" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && stopList.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:food-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Стоп-лист пуст</p>
        <p class="text-sm">Все блюда доступны для заказа</p>
      </div>

      <!-- Stop List Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Название продукта
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Терминал
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Баланс
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Дата обновления
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="item in stopList"
              :key="item.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:food" class="w-5 h-5 text-red-600" />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ item.product_name }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-900 dark:text-white">
                  {{ item.terminal_name || 'Не указан' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatBalance(item.balance) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ formatDate(item.updated_at) }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatTime(item.updated_at) }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'
import { useAuthStore } from '@/stores/auth'
import stopListService from '@/services/stop-list.service'

const organizationStore = useOrganizationStore()
const authStore = useAuthStore()

const stopList = ref([])
const loading = ref(false)
const error = ref(null)

// Проверяем наличие организации
const hasOrganization = computed(() => {
  // Проверяем прямую привязку к организации
  if (authStore.user?.organization || organizationStore.organization) {
    return true
  }
  
  // Проверяем через терминалы пользователя
  if (authStore.user?.terminals && authStore.user.terminals.length > 0) {
    // Если есть терминалы, значит организация может быть определена через них
    return true
  }
  
  // Проверяем терминалы из store
  if (organizationStore.terminals && organizationStore.terminals.length > 0) {
    return true
  }
  
  return false
})

onMounted(async () => {
  // Сначала проверяем/загружаем организацию
  if (!hasOrganization.value) {
    try {
      await organizationStore.fetchOrganization()
    } catch (err) {
      console.error('Failed to fetch organization:', err)
      // Если не удалось получить организацию напрямую, проверяем через терминалы
      if (authStore.user?.terminals && authStore.user.terminals.length > 0) {
        // Пытаемся загрузить терминалы, чтобы получить организацию
        try {
          await organizationStore.fetchTerminals()
          // Если терминалы загружены, организация должна быть определена через них
          if (organizationStore.terminals.length > 0 && organizationStore.terminals[0].organization) {
            // Организация будет определена через терминалы
          }
        } catch (termErr) {
          console.error('Failed to fetch terminals:', termErr)
        }
      }
      
      // Если организация все еще не определена
      if (!hasOrganization.value) {
        error.value = 'Не удалось определить организацию. Убедитесь, что ваш профиль привязан к организации.'
        return
      }
    }
  }

  // Если организация все еще не определена
  if (!hasOrganization.value) {
    error.value = 'Организация не определена. Обратитесь к администратору для привязки вашего профиля к организации.'
    return
  }

  await loadStopList()
})

const loadStopList = async () => {
  loading.value = true
  error.value = null

  try {
    // Проверяем наличие организации перед запросом
    if (!hasOrganization.value) {
      error.value = 'Организация не определена'
      return
    }

    const data = await stopListService.getStopList()
    
    // API может вернуть объект с results (при пагинации) или массив напрямую
    if (Array.isArray(data)) {
      stopList.value = data
    } else if (data?.results) {
      stopList.value = data.results
    } else {
      stopList.value = []
    }
  } catch (err) {
    console.error('Load stop list error:', err)
    
    // Обработка различных типов ошибок
    if (err.response?.status === 404) {
      error.value = 'Стоп-лист не найден. Возможно, организация не настроена.'
    } else if (err.response?.status === 403) {
      error.value = 'У вас нет доступа к стоп-листу'
    } else if (err.response?.status === 401) {
      error.value = 'Требуется авторизация'
    } else {
      const errorMessage = err.response?.data?.detail || 
                           err.response?.data?.error || 
                           err.message || 
                           'Не удалось загрузить стоп-лист'
      error.value = errorMessage
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatBalance = (balance) => {
  if (balance === null || balance === undefined) return '0'
  return parseFloat(balance).toFixed(2)
}
</script>
