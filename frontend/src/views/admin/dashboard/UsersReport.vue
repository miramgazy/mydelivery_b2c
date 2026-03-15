<template>
  <div class="max-w-7xl space-y-6">
    <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 flex items-center gap-2">
      <Icon icon="mdi:alert-circle" class="w-5 h-5 flex-shrink-0" />
      {{ error }}
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-16">
      <Icon icon="mdi:loading" class="w-10 h-10 animate-spin text-blue-600 mb-4" />
      <p class="text-gray-500 dark:text-gray-400">Загрузка отчёта по пользователям...</p>
    </div>

    <template v-else-if="report">
      <!-- Основные показатели -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <Icon icon="mdi:account-group" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Всего пользователей</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.totalUsers }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Icon icon="mdi:bell-check" class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Подписанных</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.subscribedCount }}</p>
              <p v-if="report.totalUsers > 0" class="text-xs text-gray-400">
                {{ percent(report.subscribedCount, report.totalUsers) }}%
              </p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <Icon icon="mdi:map-marker-check" class="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">С подтверждённым адресом</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.withVerifiedAddressCount }}</p>
              <p v-if="report.totalUsers > 0" class="text-xs text-gray-400">
                {{ percent(report.withVerifiedAddressCount, report.totalUsers) }}%
              </p>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-5 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <Icon icon="mdi:phone" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">С номером телефона</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ report.withPhoneCount }}</p>
              <p v-if="report.totalUsers > 0" class="text-xs text-gray-400">
                {{ percent(report.withPhoneCount, report.totalUsers) }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Пользователи по терминалам -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Пользователи по терминалам</h3>
        <div class="space-y-3">
          <div
            v-for="item in report.byTerminal"
            :key="item.name"
            class="flex items-center gap-3"
          >
            <span class="text-sm text-gray-700 dark:text-gray-300 min-w-[160px] truncate">{{ item.name }}</span>
            <div class="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-indigo-500 dark:bg-indigo-600 rounded-full transition-all"
                :style="{ width: barWidth(item.count) + '%' }"
              />
            </div>
            <span class="text-sm font-medium text-gray-900 dark:text-white w-12 text-right">{{ item.count }}</span>
          </div>
          <p v-if="report.byTerminal.length === 0" class="text-sm text-gray-500">Нет данных</p>
        </div>
      </div>

      <!-- Визуальное соотношение: подписанные / с адресом / с телефоном -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Структура пользователей</h3>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Подписанные на бота</p>
            <p class="text-2xl font-bold text-green-700 dark:text-green-400">{{ report.subscribedCount }}</p>
            <div class="mt-2 h-2 bg-green-200 dark:bg-green-800 rounded-full overflow-hidden">
              <div
                class="h-full bg-green-500 rounded-full"
                :style="{ width: percent(report.subscribedCount, report.totalUsers) + '%' }"
              />
            </div>
          </div>
          <div class="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">С подтверждённым адресом</p>
            <p class="text-2xl font-bold text-amber-700 dark:text-amber-400">{{ report.withVerifiedAddressCount }}</p>
            <div class="mt-2 h-2 bg-amber-200 dark:bg-amber-800 rounded-full overflow-hidden">
              <div
                class="h-full bg-amber-500 rounded-full"
                :style="{ width: percent(report.withVerifiedAddressCount, report.totalUsers) + '%' }"
              />
            </div>
          </div>
          <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">С номером телефона</p>
            <p class="text-2xl font-bold text-purple-700 dark:text-purple-400">{{ report.withPhoneCount }}</p>
            <div class="mt-2 h-2 bg-purple-200 dark:bg-purple-800 rounded-full overflow-hidden">
              <div
                class="h-full bg-purple-500 rounded-full"
                :style="{ width: percent(report.withPhoneCount, report.totalUsers) + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import {
  fetchUsersReportStatistics,
  fetchAllUsersForReport,
  aggregateUsersReport
} from '@/services/dashboard.service'

const loading = ref(true)
const error = ref(null)
const report = ref(null)

function percent(value, total) {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

function barWidth(count) {
  if (!report.value || report.value.byTerminal.length === 0) return 0
  const max = Math.max(...report.value.byTerminal.map((x) => x.count), 1)
  return Math.round((count / max) * 100)
}

async function loadReport() {
  loading.value = true
  error.value = null
  report.value = null
  try {
    report.value = await fetchUsersReportStatistics()
  } catch (err) {
    if (err.response?.status === 404) {
      try {
        const users = await fetchAllUsersForReport()
        report.value = aggregateUsersReport(users)
      } catch (fallbackErr) {
        console.error(fallbackErr)
        error.value = fallbackErr.response?.data?.detail || 'Не удалось загрузить отчёт по пользователям'
      }
    } else {
      console.error(err)
      error.value = err.response?.data?.detail || 'Не удалось загрузить отчёт по пользователям'
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadReport)
</script>
