<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Модификаторы</h2>
        </div>

        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по названию модификатора или продукта..."
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredModifiers.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:tune-variant" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Модификаторы не найдены</p>
      </div>

      <!-- Modifiers Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Название
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Продукт
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Цена
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
              v-for="modifier in filteredModifiers"
              :key="modifier?.id || Math.random()"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:tune" class="w-5 h-5 text-purple-600" />
                  <div>
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ modifier?.name || 'Без названия' }}
                    </div>
                    <div v-if="modifier?.description" class="text-xs text-gray-500 dark:text-gray-400 max-w-xs truncate">
                      {{ modifier.description }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ modifier?.product_name || '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ modifier?.price > 0 ? `+${formatPrice(modifier.price)} ₸` : 'Бесплатно' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    modifier?.is_available
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  {{ modifier?.is_available ? 'Доступен' : 'Недоступен' }}
                </span>
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
import api from '@/services/api'

const modifiers = ref([])
const loading = ref(false)
const searchQuery = ref('')

const filteredModifiers = computed(() => {
  if (!modifiers.value) return []
  
  // Filter out null/undefined items just in case
  const validModifiers = modifiers.value.filter(m => m && m.name)

  if (!searchQuery.value) {
    return validModifiers
  }

  const query = searchQuery.value.toLowerCase()
  return validModifiers.filter(m =>
    m.name.toLowerCase().includes(query) ||
    m.description?.toLowerCase().includes(query) ||
    m.product_name?.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  await loadModifiers()
})

const loadModifiers = async () => {
  loading.value = true
  try {
    const response = await api.get('/modifiers/')
    // Ensure response.data is an array and filter out invalid items if any
    modifiers.value = Array.isArray(response.data) 
      ? response.data 
      : (response.data.results || [])
  } catch (err) {
    console.error('Failed to load modifiers:', err)
  } finally {
    loading.value = false
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}
</script>
