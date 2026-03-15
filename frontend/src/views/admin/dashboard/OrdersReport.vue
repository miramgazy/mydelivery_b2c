<template>
  <div class="max-w-7xl space-y-6">
    <!-- Фильтр по датам -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Период</h3>
      <div class="flex flex-wrap items-end gap-4">
        <div class="flex flex-col gap-1">
          <label class="text-xs text-gray-500 dark:text-gray-400">Начало</label>
          <input
            v-model="dateFrom"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
          />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs text-gray-500 dark:text-gray-400">Конец</label>
          <input
            v-model="dateTo"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
          />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs text-gray-500 dark:text-gray-400">Быстрый период</label>
          <select
            v-model="presetKey"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm min-w-[200px]"
            @change="applyPreset"
          >
            <option value="today">Сегодня</option>
            <option value="yesterday">Вчера</option>
            <option value="current_week">Текущая неделя</option>
            <option value="last_week">Прошлая неделя</option>
            <option value="current_month">Текущий месяц</option>
            <option value="last_month">Прошлый месяц</option>
            <option value="current_half_year">Текущее полугодие</option>
            <option value="last_half_year">Прошлое полугодие</option>
            <option value="from_start_of_year">С начала года</option>
            <option value="last_year">Прошлый год</option>
          </select>
        </div>
        <button
          type="button"
          @click="loadReport"
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Icon v-if="loading" icon="mdi:loading" class="w-5 h-5 animate-spin" />
          <span>Применить</span>
        </button>
      </div>
    </div>

    <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 flex items-center gap-2">
      <Icon icon="mdi:alert-circle" class="w-5 h-5 flex-shrink-0" />
      {{ error }}
    </div>

    <template v-if="report">
      <!-- Карточки: количество заказов, отменённые, сумма -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <Icon icon="mdi:clipboard-list-outline" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Всего заказов</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.totalOrders }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
              <Icon icon="mdi:close-circle-outline" class="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Отменено</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.cancelledOrders }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Icon icon="mdi:currency-usd" class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Сумма (без отмен)</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatPrice(report.totalSum) }} ₸</p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <Icon icon="mdi:chart-line" class="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Активных заказов</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.totalOrders - report.cancelledOrders }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Заказы по терминалам (количество + сумма) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Количество заказов по терминалам</h3>
          <div class="space-y-3">
            <div
              v-for="item in report.byTerminal"
              :key="item.name"
              class="flex items-center gap-3"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 min-w-[120px] truncate">{{ item.name }}</span>
              <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full bg-blue-500 dark:bg-blue-600 rounded-full transition-all"
                  :style="{ width: barWidth(report.byTerminal, item.count) + '%' }"
                />
              </div>
              <span class="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">{{ item.count }}</span>
            </div>
            <p v-if="report.byTerminal.length === 0" class="text-sm text-gray-500">Нет данных</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Сумма по терминалам (без отмен)</h3>
          <div class="space-y-3">
            <div
              v-for="item in report.sumByTerminal"
              :key="item.name"
              class="flex items-center gap-3"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 min-w-[120px] truncate">{{ item.name }}</span>
              <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full bg-green-500 dark:bg-green-600 rounded-full transition-all"
                  :style="{ width: barWidthSum(report.sumByTerminal, item.sum) + '%' }"
                />
              </div>
              <span class="text-sm font-medium text-gray-900 dark:text-white w-24 text-right">{{ formatPrice(item.sum) }} ₸</span>
            </div>
            <p v-if="report.sumByTerminal.length === 0" class="text-sm text-gray-500">Нет данных</p>
          </div>
        </div>
      </div>

      <!-- По типам оплаты -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Заказы по типам оплаты</h3>
          <div class="space-y-3">
            <div
              v-for="item in report.byPaymentType"
              :key="item.name"
              class="flex items-center gap-3"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 min-w-[140px] truncate">{{ item.name }}</span>
              <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full bg-indigo-500 dark:bg-indigo-600 rounded-full transition-all"
                  :style="{ width: barWidth(report.byPaymentType, item.count) + '%' }"
                />
              </div>
              <span class="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">{{ item.count }}</span>
            </div>
            <p v-if="report.byPaymentType.length === 0" class="text-sm text-gray-500">Нет данных</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Сумма по типам оплаты</h3>
          <div class="space-y-3">
            <div
              v-for="item in report.sumByPaymentType"
              :key="item.name"
              class="flex items-center gap-3"
            >
              <span class="text-sm text-gray-700 dark:text-gray-300 min-w-[140px] truncate">{{ item.name }}</span>
              <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full bg-purple-500 dark:bg-purple-600 rounded-full transition-all"
                  :style="{ width: barWidthSum(report.sumByPaymentType, item.sum) + '%' }"
                />
              </div>
              <span class="text-sm font-medium text-gray-900 dark:text-white w-24 text-right">{{ formatPrice(item.sum) }} ₸</span>
            </div>
            <p v-if="report.sumByPaymentType.length === 0" class="text-sm text-gray-500">Нет данных</p>
          </div>
        </div>
      </div>

      <!-- Платная и бесплатная доставка -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Доставки: платные и бесплатные</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div class="flex items-center gap-4 p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
            <div class="w-14 h-14 rounded-xl bg-green-200 dark:bg-green-800/50 flex items-center justify-center">
              <Icon icon="mdi:truck-delivery" class="w-7 h-7 text-green-700 dark:text-green-300" />
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Платные доставки</p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">{{ report.paidDeliveryCount }} заказов</p>
              <p class="text-sm font-medium text-green-700 dark:text-green-400">{{ formatPrice(report.paidDeliverySum) }} ₸</p>
            </div>
          </div>
          <div class="flex items-center gap-4 p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
            <div class="w-14 h-14 rounded-xl bg-blue-200 dark:bg-blue-800/50 flex items-center justify-center">
              <Icon icon="mdi:truck-delivery" class="w-7 h-7 text-blue-700 dark:text-blue-300" />
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Бесплатные доставки</p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">{{ report.freeDeliveryCount }} заказов</p>
            </div>
          </div>
        </div>
        <div class="mt-4 flex gap-4">
          <div class="flex-1 h-4 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden flex">
            <div
              class="h-full bg-green-500 rounded-l-full"
              :style="{ width: deliveryBarWidth('paid') + '%' }"
            />
            <div
              class="h-full bg-blue-500 rounded-r-full"
              :style="{ width: deliveryBarWidth('free') + '%' }"
            />
          </div>
          <span class="text-sm text-gray-500 whitespace-nowrap">
            Платных: {{ report.paidDeliveryCount }}, бесплатных: {{ report.freeDeliveryCount }}
          </span>
        </div>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="text-center py-12 text-gray-500 dark:text-gray-400">
      Выберите период и нажмите «Применить».
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import {
  startOfDay,
  endOfDay,
  subDays,
  startOfWeek,
  endOfWeek,
  subWeeks,
  startOfMonth,
  endOfMonth,
  subMonths,
  startOfYear,
  endOfYear,
  subYears,
  format as formatDateFns
} from 'date-fns'
import { fetchOrdersForReport, aggregateOrdersReport } from '@/services/dashboard.service'

const PRESETS = {
  today: () => {
    const d = new Date()
    return { from: startOfDay(d), to: endOfDay(d) }
  },
  yesterday: () => {
    const d = subDays(new Date(), 1)
    return { from: startOfDay(d), to: endOfDay(d) }
  },
  current_week: () => {
    const d = new Date()
    return { from: startOfWeek(d, { weekStartsOn: 1 }), to: endOfWeek(d, { weekStartsOn: 1 }) }
  },
  last_week: () => {
    const d = subWeeks(new Date(), 1)
    return { from: startOfWeek(d, { weekStartsOn: 1 }), to: endOfWeek(d, { weekStartsOn: 1 }) }
  },
  current_month: () => {
    const d = new Date()
    return { from: startOfMonth(d), to: endOfMonth(d) }
  },
  last_month: () => {
    const d = subMonths(new Date(), 1)
    return { from: startOfMonth(d), to: endOfMonth(d) }
  },
  current_half_year: () => {
    const d = new Date()
    const month = d.getMonth()
    const start = new Date(d.getFullYear(), month < 6 ? 0 : 6, 1)
    const end = month < 6
      ? new Date(d.getFullYear(), 5, 30, 23, 59, 59, 999)
      : endOfYear(d)
    return { from: start, to: end }
  },
  last_half_year: () => {
    const d = new Date()
    const year = d.getFullYear()
    const month = d.getMonth()
    if (month < 6) {
      return { from: new Date(year - 1, 6, 1), to: new Date(year - 1, 11, 31, 23, 59, 59, 999) }
    }
    return { from: new Date(year, 0, 1), to: new Date(year, 5, 30, 23, 59, 59, 999) }
  },
  from_start_of_year: () => {
    const d = new Date()
    return { from: startOfYear(d), to: endOfDay(d) }
  },
  last_year: () => {
    const d = subYears(new Date(), 1)
    return { from: startOfYear(d), to: endOfYear(d) }
  }
}

function toInputDate(d) {
  return formatDateFns(d, 'yyyy-MM-dd')
}

const dateFrom = ref('')
const dateTo = ref('')
const presetKey = ref('current_month')
const loading = ref(false)
const error = ref(null)
const report = ref(null)

function applyPreset() {
  const fn = PRESETS[presetKey.value]
  if (fn) {
    const { from, to } = fn()
    dateFrom.value = toInputDate(from)
    dateTo.value = toInputDate(to)
  }
}

function formatPrice(val) {
  const n = Number(val)
  if (Number.isNaN(n)) return '0'
  return new Intl.NumberFormat('ru-RU').format(Math.round(n))
}

function barWidth(arr, value) {
  const max = Math.max(...arr.map((x) => x.count), 1)
  return Math.round((value / max) * 100)
}

function barWidthSum(arr, value) {
  const max = Math.max(...arr.map((x) => x.sum), 1)
  return Math.round((value / max) * 100)
}

function deliveryBarWidth(type) {
  if (!report.value) return 0
  const total = report.value.paidDeliveryCount + report.value.freeDeliveryCount
  if (total === 0) return type === 'paid' ? 0 : 100
  if (type === 'paid') return (report.value.paidDeliveryCount / total) * 100
  return (report.value.freeDeliveryCount / total) * 100
}

async function loadReport() {
  if (!dateFrom.value || !dateTo.value) {
    error.value = 'Укажите начальную и конечную дату'
    return
  }
  loading.value = true
  error.value = null
  report.value = null
  try {
    const orders = await fetchOrdersForReport(dateFrom.value, dateTo.value)
    report.value = aggregateOrdersReport(orders)
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить отчёт по заказам'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  applyPreset()
  loadReport()
})
</script>
