<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Заказы</h2>
          <div class="flex items-center gap-2">
            <label for="orders-search" class="sr-only">Поиск</label>
            <input
              id="orders-search"
              v-model.trim="searchQuery"
              type="search"
              placeholder="Имя, телефон, № заказа..."
              class="w-full sm:w-64 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Icon icon="mdi:magnify" class="w-5 h-5 text-gray-400 flex-shrink-0" />
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
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('order_number')"
              >
                <span class="inline-flex items-center gap-1">
                  № Заказа
                  <Icon v-if="sortKey === 'order_number'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('user_name')"
              >
                <span class="inline-flex items-center gap-1">
                  Клиент
                  <Icon v-if="sortKey === 'user_name'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('created_at')"
              >
                <span class="inline-flex items-center gap-1">
                  Дата
                  <Icon v-if="sortKey === 'created_at'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('total_price')"
              >
                <span class="inline-flex items-center gap-1">
                  Сумма
                  <Icon v-if="sortKey === 'total_price'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('payment_type_name')"
              >
                <span class="inline-flex items-center gap-1">
                  Оплата
                  <Icon v-if="sortKey === 'payment_type_name'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('terminal_name')"
              >
                <span class="inline-flex items-center gap-1">
                  Терминал
                  <Icon v-if="sortKey === 'terminal_name'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100 dark:hover:bg-gray-600"
                @click="setSort('status')"
              >
                <span class="inline-flex items-center gap-1">
                  Статус
                  <Icon v-if="sortKey === 'status'" :icon="sortOrder === 'asc' ? 'mdi:chevron-up' : 'mdi:chevron-down'" class="w-4 h-4" />
                </span>
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="order in paginatedOrders"
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
                <span class="text-sm text-gray-900 dark:text-white">
                  {{ order.terminal_name || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(order.status)">
                  {{ getStatusLabel(order.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center justify-center gap-2 flex-wrap">
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
              <!-- Uncalculated Delivery Warning -->
              <div v-if="selectedOrder && !isPickup(selectedOrder) && hasUncalculatedDelivery(selectedOrder)" class="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-start gap-3">
                <Icon icon="mdi:alert" class="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                <p class="text-sm text-amber-800 dark:text-amber-200">
                  Стоимость доставки не была рассчитана автоматически из-за отсутствия геоданных клиента! Уточните стоимость у клиента или курьера.
                </p>
              </div>

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
                  <p class="text-sm text-gray-500 dark:text-gray-400">Тип заказа</p>
                  <p class="text-base font-medium text-gray-900 dark:text-white">
                    <span v-if="isPickup(selectedOrder)" class="inline-flex items-center gap-1">
                      <Icon icon="mdi:shopping-outline" class="w-4 h-4" /> Самовывоз
                    </span>
                    <span v-else class="inline-flex items-center gap-1">
                      <Icon icon="mdi:truck-delivery-outline" class="w-4 h-4" /> Доставка
                    </span>
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Статус</p>
                  <span :class="getStatusClass(selectedOrder.status)">
                    {{ getStatusLabel(selectedOrder.status) }}
                  </span>
                  <button
                    v-if="canRepeatOrder(selectedOrder)"
                    @click="handleRepeatOrder(selectedOrder)"
                    :disabled="repeatingOrderId === selectedOrder.id"
                    class="mt-2 inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title="Повторно отправить запрос в iiko для этого заказа"
                  >
                    <Icon
                      icon="mdi:content-copy"
                      :class="{ 'animate-spin': repeatingOrderId === selectedOrder.id }"
                      class="w-4 h-4"
                    />
                    <span>Повторить</span>
                  </button>
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
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Терминал</p>
                  <p class="text-base font-medium text-gray-900 dark:text-white">
                    {{ selectedOrder.terminal_name || '—' }}
                  </p>
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
                        <td colspan="3" class="px-4 py-2 text-sm text-right text-gray-600 dark:text-gray-400">
                          Товары:
                        </td>
                        <td class="px-4 py-2 text-sm text-right text-gray-900 dark:text-white">
                          {{ formatPrice(selectedOrder.total_amount) }} ₸
                        </td>
                      </tr>
                      <tr>
                        <td colspan="3" class="px-4 py-2 text-sm text-right text-gray-600 dark:text-gray-400">
                          Доставка:
                        </td>
                        <td class="px-4 py-2 text-sm text-right text-gray-900 dark:text-white">
                          {{ selectedOrder.delivery_cost != null && Number(selectedOrder.delivery_cost) > 0 ? formatPrice(selectedOrder.delivery_cost) + ' ₸' : 'Бесплатно' }}
                        </td>
                      </tr>
                      <tr>
                        <td colspan="3" class="px-4 py-3 text-sm font-semibold text-right text-gray-900 dark:text-white">
                          Итого:
                        </td>
                        <td class="px-4 py-3 text-sm font-bold text-right text-gray-900 dark:text-white">
                          {{ formatPrice((Number(selectedOrder.total_amount) || 0) + (Number(selectedOrder.delivery_cost) || 0)) }} ₸
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
import { ref, onMounted, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrdersStore } from '@/stores/orders'
import { format } from 'date-fns'

const ordersStore = useOrdersStore()

const selectedOrder = ref(null)
const refreshingOrderId = ref(null)
const repeatingOrderId = ref(null)
const error = ref(null)

const FIVE_MINUTES_MS = 5 * 60 * 1000
const TWENTY_MINUTES_MS = 20 * 60 * 1000

/** Кнопка «Повторить» доступна для заказа со статусом «В процессе iiko»,
 *  если с момента создания прошло не менее 5 минут и не более 20 минут
 */
function canRepeatOrder(order) {
  if (!order || order.status !== 'InProgress') return false
  const created = new Date(order.created_at).getTime()
  const age = Date.now() - created
  return age >= FIVE_MINUTES_MS && age <= TWENTY_MINUTES_MS
}

const loading = computed(() => ordersStore.loading)
const orders = computed(() => ordersStore.orders || [])

const searchQuery = ref('')
const sortKey = ref('created_at')
const sortOrder = ref('desc')

const setSort = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const filteredOrders = computed(() => {
  const q = (searchQuery.value || '').toLowerCase()
  if (!q) return orders.value
  return orders.value.filter((order) => {
    const name = (order.user_name || '').toLowerCase()
    const phone = (order.phone || '').replace(/\D/g, '')
    const orderNum = (order.order_number || order.id || '').toString().toLowerCase()
    const qNorm = q.replace(/\D/g, '')
    return (
      name.includes(q) ||
      (order.phone || '').toLowerCase().includes(q) ||
      (qNorm && phone.includes(qNorm)) ||
      orderNum.includes(q)
    )
  })
})

const sortedOrders = computed(() => {
  const list = [...filteredOrders.value]
  const key = sortKey.value
  const asc = sortOrder.value === 'asc'
  list.sort((a, b) => {
    let va = a[key]
    let vb = b[key]
    if (key === 'created_at') {
      va = new Date(va || 0).getTime()
      vb = new Date(vb || 0).getTime()
    }
    if (key === 'total_price' || key === 'total_amount') {
      va = Number(va) || 0
      vb = Number(vb) || 0
    }
    if (key === 'order_number') {
      va = (va || a.id || '').toString()
      vb = (vb || b.id || '').toString()
    }
    if (va == null) return asc ? 1 : -1
    if (vb == null) return asc ? -1 : 1
    if (typeof va === 'string' && typeof vb === 'string') {
      const c = va.localeCompare(vb, 'ru')
      return asc ? c : -c
    }
    if (va < vb) return asc ? -1 : 1
    if (va > vb) return asc ? 1 : -1
    return 0
  })
  return list
})

const PAGINATION_WINDOW = 12
const PAGINATION_LAST = 3

const currentPage = ref(1)
const perPage = ref(20)
const paginationWindowStart = ref(1)

const totalOrders = computed(() => sortedOrders.value.length)
const totalPages = computed(() => {
  if (!totalOrders.value) return 1
  return Math.max(1, Math.ceil(totalOrders.value / perPage.value))
})

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return sortedOrders.value.slice(start, start + perPage.value)
})

/** Номера страниц для отображения: до 15 — все; больше 15 — окно 12 + "..." + последние 3, прокрутка << >> */
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

watch([orders, perPage, searchQuery, sortKey, sortOrder], () => {
  currentPage.value = 1
  paginationWindowStart.value = 1
})
watch(totalPages, (newTotal) => {
  if (newTotal <= 15) paginationWindowStart.value = 1
  else paginationWindowStart.value = Math.min(paginationWindowStart.value, newTotal - 14)
})

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

const handleRepeatOrder = async (order) => {
  repeatingOrderId.value = order.id
  error.value = null

  try {
    const updated = await ordersStore.repeatOrder(order.id)
    selectedOrder.value = updated
    await loadOrders()
  } catch (err) {
    error.value = ordersStore.error || 'Не удалось повторить заказ'
  } finally {
    repeatingOrderId.value = null
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
    'Success': 'Создан в iiko',
    'SentToBackupWebhook': 'Отправлен на резервный вебхук',
    // Статусы из iiko (order.status после creationStatus=Success)
    'Cancelled': 'Отменен',
    'Confirmed': 'Подтвержден',
    'Cooking': 'Готовится',
    'ReadyForCooking': 'Готов к приготовлению',
    'Delivered': 'Доставлен',
    'Closed': 'Закрыт',
    'Unconfirmed': 'Не подтвержден'
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
    'Success': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    'SentToBackupWebhook': 'bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400',
    'Cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    'Confirmed': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
    'Cooking': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
    'ReadyForCooking': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
    'Delivered': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    'Closed': 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
    'Unconfirmed': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
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

const isPickup = (order) => {
  if (!order) return false
  return !order.delivery_address && !order.delivery_address_full && !order.latitude && !order.longitude
}

const hasUncalculatedDelivery = (order) => {
  if (!order || !order.comment) return false
  return order.comment.includes('Стоимость доставки не расчитан из за отсутствие геоданных')
}
</script>
