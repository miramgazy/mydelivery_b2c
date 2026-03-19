<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">Продукты</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Активное меню организации (то же, что в TMA)</p>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex gap-4">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по названию..."
            class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <select
            v-model="categoryFilter"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Все категории</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <select
            v-model="availabilityFilter"
            class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Все статусы</option>
            <option value="true">Доступно</option>
            <option value="false">Недоступно</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="filteredProducts.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:food-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Продукты не найдены</p>
      </div>

      <!-- Products Table -->
      <div v-else>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Фото
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Название
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Категория
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Цена
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Модификаторы
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Статус
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="product in paginatedProducts"
                :key="product.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="w-12 h-12 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                  <img
                    v-if="product.image_url"
                    :src="product.image_url"
                    :alt="product.name"
                    class="w-full h-full object-cover"
                  />
                  <Icon v-else icon="mdi:food" class="w-6 h-6 text-gray-400" />
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ product.name }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 max-w-xs truncate">
                  {{ product.description }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ product.category?.subgroup_name || '-' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatPrice(product.price) }} ₸
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="product.has_modifiers"
                  class="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 rounded-md text-xs"
                >
                  <Icon icon="mdi:tune" class="w-3 h-3" />
                  Есть
                </span>
                <span v-else class="text-sm text-gray-400">-</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    product.is_available
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  {{ product.is_available ? 'Доступен' : 'Недоступен' }}
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
import { useProductsStore } from '@/stores/products'

const PAGINATION_WINDOW = 12
const PAGINATION_LAST = 3

const productsStore = useProductsStore()

const searchQuery = ref('')
const categoryFilter = ref('')
const availabilityFilter = ref('')

const currentPage = ref(1)
const perPage = ref(20)
const paginationWindowStart = ref(1)

const loading = computed(() => productsStore.loading)
const products = computed(() => productsStore.products || [])

const categories = computed(() => {
  const cats = new Map()
  products.value.forEach(product => {
    if (product.category) {
      cats.set(product.category.subgroup_id, {
        id: product.category.subgroup_id,
        name: product.category.subgroup_name
      })
    }
  })
  return Array.from(cats.values())
})

const filteredProducts = computed(() => {
  let filtered = products.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.description?.toLowerCase().includes(query)
    )
  }

  // Category filter
  if (categoryFilter.value) {
    filtered = filtered.filter(p => p.category?.subgroup_id === categoryFilter.value)
  }

  // Availability filter
  if (availabilityFilter.value !== '') {
    const isAvailable = availabilityFilter.value === 'true'
    filtered = filtered.filter(p => p.is_available === isAvailable)
  }

  return filtered
})

const totalProducts = computed(() => filteredProducts.value.length)
const totalPages = computed(() => {
  if (!totalProducts.value) return 1
  return Math.max(1, Math.ceil(totalProducts.value / perPage.value))
})

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredProducts.value.slice(start, start + perPage.value)
})

/** Номера страниц: до 15 — все; больше 15 — окно 12 + "..." + последние 3, прокрутка << >> */
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
const canGoNext = computed(() =>
  totalPages.value > 15 && paginationWindowStart.value <= totalPages.value - 15
)

function goPrevWindow() {
  if (!canGoPrev.value) return
  paginationWindowStart.value = Math.max(1, paginationWindowStart.value - PAGINATION_WINDOW)
}

function goNextWindow() {
  if (!canGoNext.value) return
  paginationWindowStart.value = Math.min(
    totalPages.value - 14,
    paginationWindowStart.value + PAGINATION_WINDOW
  )
}

watch([filteredProducts, perPage, searchQuery, categoryFilter, availabilityFilter], () => {
  currentPage.value = 1
  paginationWindowStart.value = 1
})
watch(totalPages, (newTotal) => {
  if (newTotal <= 15) paginationWindowStart.value = 1
  else paginationWindowStart.value = Math.min(paginationWindowStart.value, newTotal - 14)
})

onMounted(async () => {
  await loadProducts()
})

const loadProducts = async () => {
  try {
    await productsStore.fetchProducts()
  } catch (err) {
    console.error('Failed to load products:', err)
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}
</script>
