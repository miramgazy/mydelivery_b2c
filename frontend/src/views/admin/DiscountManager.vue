<template>
  <div class="max-w-6xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Скидки</h2>
          <div class="flex items-center gap-3">
            <button
              @click="handleSync"
              :disabled="syncLoading"
              class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
                     text-white font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              <Icon
                :icon="syncLoading ? 'mdi:loading' : 'mdi:sync'"
                :class="{ 'animate-spin': syncLoading }"
                class="w-5 h-5"
              />
              Синхронизировать
            </button>
            <button
              @click="handleClearInactive"
              :disabled="!hasInactiveDiscounts"
              class="flex items-center gap-2 px-4 py-2.5 bg-red-600 hover:bg-red-700
                     text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon icon="mdi:delete-sweep" class="w-5 h-5" />
              Удалить неактивные
            </button>
          </div>
        </div>
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
      <div v-if="loading && discounts.length === 0" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && discounts.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:percent-outline" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Скидки не найдены</p>
        <p class="text-sm mb-4">Нажмите «Синхронизировать» для загрузки скидок из IIKO</p>
      </div>

      <!-- Discounts Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Название
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Организация
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Тип (Mode)
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Процент
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="discount in discounts"
              :key="discount.id || discount.external_id"
              :class="[
                'transition-colors',
                !discount.is_active ? 'opacity-50' : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
              ]"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:percent" class="w-5 h-5 text-blue-600" />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ discount.name }}
                  </span>
                  <span
                    v-if="!discount.is_active"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300"
                  >
                    Архив
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ discount.organization_name || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ discount.mode || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ formatPercent(discount.percent) }}
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
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useNotificationStore } from '@/stores/notifications'
import discountService from '@/services/discount.service'

const discounts = ref([])
const loading = ref(false)
const syncLoading = ref(false)
const error = ref(null)

const hasInactiveDiscounts = computed(() =>
  discounts.value.some((d) => d.is_active === false)
)

const loadDiscounts = async () => {
  loading.value = true
  error.value = null
  try {
    discounts.value = await discountService.getDiscounts()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Не удалось загрузить скидки'
  } finally {
    loading.value = false
  }
}

const handleSync = async () => {
  syncLoading.value = true
  error.value = null
  try {
    await discountService.syncDiscounts()
    const notificationStore = useNotificationStore()
    notificationStore.show('Скидки успешно синхронизированы')
    await loadDiscounts()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Не удалось синхронизировать скидки'
  } finally {
    syncLoading.value = false
  }
}

const handleClearInactive = async () => {
  if (!hasInactiveDiscounts.value) return
  const confirmed = window.confirm(
    'Вы уверены, что хотите удалить все неактивные скидки? Это действие нельзя отменить.'
  )
  if (!confirmed) return

  error.value = null
  try {
    const result = await discountService.clearInactiveDiscounts()
    const notificationStore = useNotificationStore()
    notificationStore.show(result.message || 'Неактивные скидки удалены')
    await loadDiscounts()
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.detail || 'Не удалось удалить неактивные скидки'
  }
}

const formatPercent = (value) => {
  if (value == null || value === '') return '—'
  const num = parseFloat(value)
  return Number.isNaN(num) ? '—' : `${num}%`
}

onMounted(() => {
  loadDiscounts()
})
</script>
