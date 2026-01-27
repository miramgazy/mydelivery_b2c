<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Заказы</h2>
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
      <div v-if="loading && orders.length === 0" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && orders.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:clipboard-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Заказов пока нет</p>
      </div>

      <!-- Orders Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                № Заказа
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Клиент
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Дата
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Сумма
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Оплата
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="order in orders"
              :key="order.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-mono font-medium text-gray-900 dark:text-white">
                  #{{ order.order_number || order.id.slice(0, 8) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ order.user_name || 'Гость' }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ order.phone || '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ formatDate(order.created_at) }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatTime(order.created_at) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-semibold text-gray-900 dark:text-white">
                  {{ formatPrice(order.total_price) }} ₸
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex flex-col gap-1">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ order.payment_type_name || 'Не указан' }}
                  </span>
                  <span
                    v-if="order.payment_type_system_type === 'remote_payment' && extractPhoneFromComment(order.comment)"
                    class="text-xs text-blue-600 dark:text-blue-400"
                  >
                    📱 {{ extractPhoneFromComment(order.comment) }}
                  </span>
                  <span
                    v-else-if="order.payment_type_system_type"
                    class="text-xs text-gray-500 dark:text-gray-400"
                  >
                    {{ getSystemTypeLabel(order.payment_type_system_type) }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(order.status)">
                  {{ getStatusLabel(order.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center justify-center gap-2">
                  <button
                    @click="handleViewOrder(order)"
                    class="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                  >
                    <Icon icon="mdi:eye" class="w-4 h-4" />
                    <span>Открыть</span>
                  </button>
                  <button
                    @click="handleRefreshStatus(order)"
                    :disabled="refreshingOrderId === order.id"
                    class="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title="Обновить статус в IIKO"
                  >
                    <Icon
                      icon="mdi:refresh"
                      :class="{ 'animate-spin': refreshingOrderId === order.id }"
                      class="w-5 h-5"
                    />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <Teleport to="body">
      <div
        v-if="selectedOrder"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="selectedOrder = null"
      >
        <div class="flex min-h-screen items-center justify-center p-4">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/50 transition-opacity"></div>

          <!-- Modal -->
          <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full">
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                Заказ #{{ selectedOrder.order_number || selectedOrder.id.slice(0, 8) }}
              </h3>
              <button
                @click="selectedOrder = null"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Icon icon="mdi:close" class="w-6 h-6" />
              </button>
            </div>

            <!-- Content -->
            <div class="p-6 space-y-6">
              <!-- Order Info -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Клиент</p>
                  <p class="text-base font-medium text-gray-900 dark:text-white">
                    {{ selectedOrder.user_name || 'Гость' }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Телефон</p>
                  <p class="text-base font-medium text-gray-900 dark:text-white">
                    {{ selectedOrder.phone || '-' }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Дата создания</p>
                  <p class="text-base font-medium text-gray-900 dark:text-white">
                    {{ formatDate(selectedOrder.created_at) }} {{ formatTime(selectedOrder.created_at) }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Статус</p>
                  <span :class="getStatusClass(selectedOrder.status)">
                    {{ getStatusLabel(selectedOrder.status) }}
                  </span>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Тип оплаты</p>
                  <div class="flex flex-col gap-1">
                    <p class="text-base font-medium text-gray-900 dark:text-white">
                      {{ selectedOrder.payment_type_name || 'Не указан' }}
                    </p>
                    <span
                      v-if="selectedOrder.payment_type_system_type === 'remote_payment' && extractPhoneFromComment(selectedOrder.comment)"
                      class="text-sm text-blue-600 dark:text-blue-400"
                    >
                      📱 Номер для Kaspi: {{ extractPhoneFromComment(selectedOrder.comment) }}
                    </span>
                    <span
                      v-else-if="selectedOrder.payment_type_system_type"
                      class="text-xs text-gray-500 dark:text-gray-400"
                    >
                      {{ getSystemTypeLabel(selectedOrder.payment_type_system_type) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Delivery Address -->
              <div v-if="selectedOrder.delivery_address_full || selectedOrder.delivery_address">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Адрес доставки</p>
                <p class="text-base text-gray-900 dark:text-white">
                  {{ selectedOrder.delivery_address_full || formatAddress(selectedOrder.delivery_address) }}
                </p>
              </div>

              <!-- Comment -->
              <div v-if="selectedOrder.comment">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Комментарий</p>
                <p class="text-base text-gray-900 dark:text-white whitespace-pre-wrap">
                  {{ selectedOrder.comment }}
                </p>
              </div>

              <!-- Order Items -->
              <div>
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Состав заказа</h4>
                <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                  <table class="w-full">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Продукт</th>
                        <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-400">Кол-во</th>
                        <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Цена</th>
                        <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Сумма</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                      <tr v-for="item in selectedOrder.items" :key="item.id">
                        <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                          <div class="font-medium">{{ item.product_name }}</div>
                          <div v-if="item.modifiers?.length > 0" class="text-xs text-gray-500 mt-1">
                            <span v-for="(mod, index) in item.modifiers" :key="mod.id">
                              {{ mod.modifier_name }}{{ mod.quantity > 1 ? ` x${mod.quantity}` : '' }}{{ index < item.modifiers.length - 1 ? ', ' : '' }}
                            </span>
                          </div>
                        </td>
                        <td class="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300">
                          {{ item.quantity }}
                        </td>
                        <td class="px-4 py-3 text-sm text-right text-gray-700 dark:text-gray-300">
                          {{ formatPrice(item.price) }} ₸
                        </td>
                        <td class="px-4 py-3 text-sm text-right font-medium text-gray-900 dark:text-white">
                          {{ formatPrice(item.price * item.quantity) }} ₸
                        </td>
                      </tr>
                    </tbody>
                    <tfoot class="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <td colspan="3" class="px-4 py-3 text-sm font-semibold text-right text-gray-900 dark:text-white">
                          Итого:
                        </td>
                        <td class="px-4 py-3 text-sm font-bold text-right text-gray-900 dark:text-white">
                          {{ formatPrice(selectedOrder.total_price) }} ₸
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrdersStore } from '@/stores/orders'
import { format } from 'date-fns'

const ordersStore = useOrdersStore()

const selectedOrder = ref(null)
const refreshingOrderId = ref(null)
const error = ref(null)

const loading = computed(() => ordersStore.loading)
const orders = computed(() => ordersStore.orders || [])

onMounted(async () => {
  await loadOrders()
})

const loadOrders = async () => {
  error.value = null
  try {
    await ordersStore.fetchOrders()
  } catch (err) {
    error.value = 'Не удалось загрузить заказы'
  }
}

const handleViewOrder = async (order) => {
  try {
    const fullOrder = await ordersStore.fetchOrderDetail(order.id)
    selectedOrder.value = fullOrder
  } catch (err) {
    error.value = 'Не удалось загрузить детали заказа'
  }
}

const handleRefreshStatus = async (order) => {
  refreshingOrderId.value = order.id
  error.value = null

  try {
    // Call API to refresh order status from iiko
    // await ordersStore.refreshOrderStatus(order.id)
    console.log('Refreshing status for order:', order.id)
    // For now, just reload orders
    await loadOrders()
  } catch (err) {
    error.value = 'Не удалось обновить статус заказа'
  } finally {
    refreshingOrderId.value = null
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return format(new Date(dateString), 'dd.MM.yyyy')
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return format(new Date(dateString), 'HH:mm')
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const formatAddress = (address) => {
  if (!address) return '-'
  const parts = []
  if (address.city_name) parts.push(address.city_name)
  if (address.street_name) parts.push(address.street_name)
  if (address.house) parts.push(`д. ${address.house}`)
  if (address.flat) parts.push(`кв. ${address.flat}`)
  return parts.join(', ') || '-'
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': 'Ожидает',
    'confirmed': 'Подтвержден',
    'preparing': 'Готовится',
    'ready': 'Готов',
    'delivering': 'Доставляется',
    'completed': 'Завершен',
    'cancelled': 'Отменен',
    'error': 'Ошибка',
    'InProgress': 'В процессе iiko',
    'Success': 'Создан в iiko'
  }
  return labels[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    'confirmed': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    'preparing': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
    'ready': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    'delivering': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    'error': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    'InProgress': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    'Success': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
  }
  return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${classes[status] || ''}`
}

const getSystemTypeLabel = (systemType) => {
  const labels = {
    'cash': 'Наличные',
    'remote_payment': 'Удаленный счет',
    'card_on_delivery': 'Карта при получении'
  }
  return labels[systemType] || systemType
}

const extractPhoneFromComment = (comment) => {
  if (!comment) return null
  // Ищем паттерн "Выставить на номер: +7..." или "номер: +7..."
  // Формат комментария: "Оплата: Удаленный счет. Выставить на номер: +77771234567."
  const patterns = [
    /номер[:\s]+([+\d\s\-()]+)/i,
    /на номер[:\s]+([+\d\s\-()]+)/i,
    /номер[:\s]+([+\d]+)/i
  ]
  
  for (const pattern of patterns) {
    const match = comment.match(pattern)
    if (match && match[1]) {
      const phone = match[1].trim().replace(/[^\d+]/g, '')
      if (phone && phone.length >= 10) {
        return phone
      }
    }
  }
  return null
}
</script>
