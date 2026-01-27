<template>
  <div class="max-w-6xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Типы оплат</h2>
          <div class="flex items-center gap-3">
            <button
              @click="openCreateModal"
              class="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700
                     text-white font-medium rounded-lg transition-colors"
            >
              <Icon icon="mdi:plus" class="w-5 h-5" />
              Добавить тип оплаты
            </button>
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
        <p class="text-sm mb-4">Нажмите "Добавить тип оплаты" для создания нового или "Загрузить из IIKO" для импорта</p>
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
                Тип iiko
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Системный тип
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Действия
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
                  {{ paymentType.iiko_payment_id || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ getPaymentTypeLabel(paymentType.payment_type) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ getSystemTypeLabel(paymentType.system_type) || 'Не задан' }}
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
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="openEditModal(paymentType)"
                  class="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                  title="Редактировать"
                >
                  <Icon icon="mdi:pencil" class="w-5 h-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="closeModal"
      >
        <div class="flex min-h-screen items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50 transition-opacity"></div>

          <!-- Modal -->
          <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full">
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                {{ editingPaymentType ? 'Редактировать тип оплаты' : 'Создать тип оплаты' }}
              </h3>
              <button
                @click="closeModal"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Icon icon="mdi:close" class="w-6 h-6" />
              </button>
            </div>

            <!-- Content -->
            <div class="p-6 space-y-6">
              <form @submit.prevent="savePaymentType" class="space-y-4">
                <!-- Payment Name -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Название <span class="text-red-500">*</span>
                  </label>
                  <input
                    v-model="form.payment_name"
                    type="text"
                    required
                    placeholder="Например, Kaspi Red"
                    class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <!-- Payment Type (iiko) -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Тип iiko <span class="text-red-500">*</span>
                  </label>
                  <select
                    v-model="form.payment_type"
                    required
                    class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="CASH">CASH</option>
                    <option value="CARD">CARD</option>
                    <option value="ONLINE">ONLINE</option>
                    <option value="CREDIT">CREDIT</option>
                    <option value="EXTERNAL">EXTERNAL</option>
                  </select>
                </div>

                <!-- System Type -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Системный тип <span class="text-red-500">*</span>
                  </label>
                  <select
                    v-model="form.system_type"
                    required
                    class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="" disabled>Выберите системный тип</option>
                    <option value="cash">Наличные</option>
                    <option value="remote_payment">Удаленный счет (Kaspi)</option>
                    <option value="card_on_delivery">Карта при получении</option>
                  </select>
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Системный тип определяет логику обработки оплаты на фронтенде
                  </p>
                </div>

                <!-- Is Active -->
                <div class="flex items-center gap-3">
                  <input
                    id="is-active"
                    v-model="form.is_active"
                    type="checkbox"
                    class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label for="is-active" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Активен
                  </label>
                </div>

                <!-- Error Message -->
                <div v-if="modalError" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <div class="flex items-center gap-2 text-red-800 dark:text-red-200 text-sm">
                    <Icon icon="mdi:alert-circle" class="w-5 h-5" />
                    <span>{{ modalError }}</span>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    @click="closeModal"
                    class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    :disabled="modalLoading"
                    class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Icon
                      v-if="modalLoading"
                      icon="mdi:loading"
                      class="w-5 h-5 animate-spin"
                    />
                    <span>{{ modalLoading ? 'Сохранение...' : (editingPaymentType ? 'Сохранить изменения' : 'Создать') }}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'
import api from '@/services/api'

const organizationStore = useOrganizationStore()

const successMessage = ref('')
const error = ref(null)
const loading = computed(() => organizationStore.loading)
const paymentTypes = computed(() => organizationStore.paymentTypes || [])

// Modal state
const showModal = ref(false)
const editingPaymentType = ref(null)
const modalLoading = ref(false)
const modalError = ref('')

const form = ref({
  payment_name: '',
  payment_type: 'CASH',
  system_type: '',
  is_active: true,
})

// Reset form when modal closes
watch(showModal, (newVal) => {
  if (!newVal) {
    editingPaymentType.value = null
    modalError.value = ''
    form.value = {
      payment_name: '',
      payment_type: 'CASH',
      system_type: '',
      is_active: true,
    }
  }
})

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

const getSystemTypeLabel = (type) => {
  const labels = {
    'cash': 'Наличные',
    'remote_payment': 'Удаленный счет',
    'card_on_delivery': 'Карта при получении'
  }
  return labels[type] || null
}

const openCreateModal = () => {
  editingPaymentType.value = null
  form.value = {
    payment_name: '',
    payment_type: 'CASH',
    system_type: '',
    is_active: true,
  }
  modalError.value = ''
  showModal.value = true
}

const openEditModal = (paymentType) => {
  editingPaymentType.value = paymentType
  form.value = {
    payment_name: paymentType.name || paymentType.payment_name || '',
    payment_type: paymentType.payment_type || 'CASH',
    system_type: paymentType.system_type || '',
    is_active: paymentType.is_active !== undefined ? paymentType.is_active : true,
  }
  modalError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const savePaymentType = async () => {
  modalError.value = ''
  modalLoading.value = true

  try {
    // Убеждаемся, что организация загружена
    if (!organizationStore.organization) {
      await organizationStore.fetchOrganization()
    }
    
    const org = organizationStore.organization
    const organizationId = org?.id || org?.org_id

    if (!organizationId) {
      modalError.value = 'Организация не найдена. Пожалуйста, обновите страницу.'
      modalLoading.value = false
      return
    }

    const payload = {
      payment_name: form.value.payment_name.trim(),
      payment_type: form.value.payment_type,
      system_type: form.value.system_type,
      is_active: form.value.is_active,
      organization: organizationId,
    }

    if (editingPaymentType.value) {
      // Update existing
      await api.patch(`/payment-types/${editingPaymentType.value.id}/`, payload)
      successMessage.value = 'Тип оплаты успешно обновлен'
    } else {
      // Create new
      await api.post('/payment-types/', payload)
      successMessage.value = 'Тип оплаты успешно создан'
    }
    
    // Обновляем список типов оплаты
    await loadPaymentTypes()
    
    // Закрываем модальное окно
    closeModal()

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    console.error('Save payment type error', err)
    console.error('Error response:', err.response?.data)
    modalError.value =
      err.response?.data?.detail ||
      err.response?.data?.error ||
      err.response?.data?.organization?.[0] ||
      err.response?.data?.payment_name?.[0] ||
      err.response?.data?.system_type?.[0] ||
      'Не удалось сохранить тип оплаты'
  } finally {
    modalLoading.value = false
  }
}
</script>
