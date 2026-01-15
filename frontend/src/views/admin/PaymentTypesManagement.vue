<template>
  <div class="max-w-6xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Типы оплат</h2>
          <button
            @click="handleLoadFromIiko"
            :disabled="loading"
            class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
                   text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            <Icon
              :icon="loading ? 'mdi:loading' : 'mdi:download'"
              :class="{ 'animate-spin': loading }"
              class="w-5 h-5"
            />
            Загрузить из IIKO
          </button>
        </div>
      </div>

      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="mx-6 mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-green-800 dark:text-green-200">
          <Icon icon="mdi:check-circle" class="w-5 h-5" />
          <span>{{ successMessage }}</span>
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
      <div v-if="loading && paymentTypes.length === 0" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && paymentTypes.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:credit-card-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Типы оплат не найдены</p>
        <p class="text-sm">Нажмите "Загрузить из IIKO" для импорта типов оплат</p>
      </div>

      <!-- Payment Types Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Название
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                ID в iiko
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Тип
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="paymentType in paymentTypes"
              :key="paymentType.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:credit-card" class="w-5 h-5 text-green-600" />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ paymentType.name }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-500 dark:text-gray-400 font-mono">
                  {{ paymentType.iiko_payment_id }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ getPaymentTypeLabel(paymentType.payment_type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    paymentType.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  {{ paymentType.is_active ? 'Активен' : 'Неактивен' }}
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
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const successMessage = ref('')
const error = ref(null)

const loading = computed(() => organizationStore.loading)
const paymentTypes = computed(() => organizationStore.paymentTypes || [])

onMounted(async () => {
  await loadPaymentTypes()
})

const loadPaymentTypes = async () => {
  error.value = null
  try {
    await organizationStore.fetchPaymentTypes()
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось загрузить типы оплат'
  }
}

const handleLoadFromIiko = async () => {
  error.value = null
  successMessage.value = ''

  try {
    const result = await organizationStore.loadPaymentTypesFromIiko()
    successMessage.value = result.message || 'Типы оплат успешно загружены из IIKO'

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось загрузить типы оплат из IIKO'
  }
}

const getPaymentTypeLabel = (type) => {
  const labels = {
    'CASH': 'Наличные',
    'CARD': 'Карта',
    'ONLINE': 'Онлайн',
    'CREDIT': 'Кредит',
    'EXTERNAL': 'Внешний'
  }
  return labels[type] || type
}
</script>
