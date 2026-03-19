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
      <div v-else>
        <div class="overflow-x-auto">
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
                v-for="modifier in paginatedModifiers"
                :key="modifier.id"
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

        <!-- Pagination -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <span>Показывать по:</span>
            <select
              v-model.number="perPage"
              class="border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
            >
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
          </div>

          <div class="flex items-center gap-1 flex-wrap justify-center">
            <button
              type="button"
              aria-label="Предыдущий блок страниц"
              :disabled="!canGoPrev"
              @click="goPrevWindow"
              class="min-w-[2.25rem] h-9 px-2 rounded-md text-sm font-medium border border-gray-300 dark:border-gray-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              &laquo;
            </button>

            <template v-for="(item, idx) in visiblePageNumbers" :key="item.type === 'ellipsis' ? `ellipsis-${idx}` : item.num">
              <span
                v-if="item.type === 'ellipsis'"
                class="min-w-[2.25rem] h-9 flex items-center justify-center text-gray-500 dark:text-gray-400"
              >
                &hellip;
              </span>
              <button
                v-else
                type="button"
                @click="currentPage = item.num"
                class="min-w-[2.25rem] h-9 px-3 rounded-md text-sm font-medium border transition-colors"
                :class="currentPage === item.num
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'"
              >
                {{ item.num }}
              </button>
            </template>

            <button
              type="button"
              aria-label="Следующий блок страниц"
              :disabled="!canGoNext"
              @click="goNextWindow"
              class="min-w-[2.25rem] h-9 px-2 rounded-md text-sm font-medium border border-gray-300 dark:border-gray-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              &raquo;
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import api from '@/services/api'

const PAGINATION_WINDOW = 12
const PAGINATION_LAST = 3

const modifiers = ref([])
const loading = ref(false)
const searchQuery = ref('')

const currentPage = ref(1)
const perPage = ref(20)
const paginationWindowStart = ref(1)

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

const totalModifiers = computed(() => filteredModifiers.value.length)
const totalPages = computed(() => {
  if (!totalModifiers.value) return 1
  return Math.max(1, Math.ceil(totalModifiers.value / perPage.value))
})

const paginatedModifiers = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredModifiers.value.slice(start, start + perPage.value)
})

const visiblePageNumbers = computed(() => {
  const total = totalPages.value
  if (total <= 15) {
    return Array.from({ length: total }, (_, i) => ({ type: 'page', num: i + 1 }))
  }

  const start = paginationWindowStart.value
  const lastStart = total - PAGINATION_LAST + 1
  const firstEnd = Math.min(start + PAGINATION_WINDOW - 1, lastStart - 1)

  const list = []
  for (let p = start; p <= firstEnd; p++) list.push({ type: 'page', num: p })

  if (firstEnd < lastStart - 1) {
    list.push({ type: 'ellipsis' })
  }

  for (let p = lastStart; p <= total; p++) list.push({ type: 'page', num: p })
  return list
})

const canGoPrev = computed(() => totalPages.value > 15 && paginationWindowStart.value > 1)
const canGoNext = computed(() => totalPages.value > 15 && paginationWindowStart.value <= totalPages.value - 15)

function goPrevWindow() {
  if (!canGoPrev.value) return
  paginationWindowStart.value = Math.max(1, paginationWindowStart.value - PAGINATION_WINDOW)
}

function goNextWindow() {
  if (!canGoNext.value) return
  paginationWindowStart.value = Math.min(totalPages.value - 14, paginationWindowStart.value + PAGINATION_WINDOW)
}

onMounted(async () => {
  await loadModifiersAllPages()
})

watch([searchQuery, perPage], () => {
  currentPage.value = 1
  paginationWindowStart.value = 1
})

watch(totalPages, (newTotal) => {
  if (newTotal <= 15) paginationWindowStart.value = 1
  else paginationWindowStart.value = Math.min(paginationWindowStart.value, newTotal - 14)
})

const loadModifiersAllPages = async () => {
  loading.value = true
  try {
    modifiers.value = []

    // Загружаем все страницы, потому что API обычно возвращает пагинированные данные.
    // Это сохраняет работу поиска по всем модификаторам.
    let page = 1
    const pageSize = 50

    while (true) {
      const response = await api.get('/modifiers/', {
        params: { page, page_size: pageSize }
      })

      if (Array.isArray(response.data)) {
        modifiers.value = response.data
        break
      }

      const results = response.data?.results || []
      modifiers.value.push(...results)

      const totalCount = response.data?.count
      if (results.length === 0) break
      if (typeof totalCount === 'number' && modifiers.value.length >= totalCount) break

      page += 1
    }
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
