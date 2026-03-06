<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Мультиязычные рассылки</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Планируйте отложенные рассылки по подписчикам Telegram и смотрите статистику.
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        @click="openCreateModal"
      >
        Создать рассылку
      </button>
    </div>

    <div class="bg-white dark:bg-gray-800 shadow-sm rounded-xl overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-900/40">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Название</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Создана</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Отправка</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Статус</th>
            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Статистика</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="mailing in mailings"
            :key="mailing.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700/40 cursor-pointer"
            @click="onRowClick(mailing)"
          >
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
              {{ mailing.id }}
            </td>
            <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
              {{ mailing.title }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(mailing.created_at) }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(mailing.scheduled_at) }}
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                :class="statusBadgeClass(mailing.status)"
              >
                {{ statusLabel(mailing.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-300">
              <span v-if="mailing.total_recipients">
                {{ mailing.sent_ru + mailing.sent_kz }} / {{ mailing.total_recipients }}
              </span>
              <span v-else>-</span>
            </td>
          </tr>
          <tr v-if="!mailings.length">
            <td colspan="6" class="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
              Рассылок пока нет. Нажмите «Создать рассылку», чтобы запланировать первую.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <CreateMailingModal
      v-if="isCreateOpen"
      @close="isCreateOpen = false"
      @created="handleCreated"
    />

    <MailingAnalyticsModal
      v-if="selectedMailing"
      :mailing="selectedMailing"
      @close="selectedMailing = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import CreateMailingModal from '@/components/admin/mailings/CreateMailingModal.vue'
import MailingAnalyticsModal from '@/components/admin/mailings/MailingAnalyticsModal.vue'

const mailings = ref([])
const isCreateOpen = ref(false)
const selectedMailing = ref(null)

const fetchMailings = async () => {
  const { data } = await api.get('/organizations/mailings/')
  // DRF по умолчанию возвращает пагинированный ответ {count, results, ...}
  mailings.value = Array.isArray(data) ? data : (data.results || [])
}

const openCreateModal = () => {
  isCreateOpen.value = true
}

const handleCreated = () => {
  isCreateOpen.value = false
  fetchMailings()
}

const onRowClick = (mailing) => {
  if (mailing.status === 'done' || mailing.status === 'ERROR' || mailing.status === 'error') {
    selectedMailing.value = mailing
  }
}

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

const statusLabel = (status) => {
  const map = {
    draft: 'Черновик',
    scheduled: 'Запланирована',
    in_progress: 'В процессе',
    done: 'Завершена',
    error: 'Ошибка',
  }
  return map[status] || status
}

const statusBadgeClass = (status) => {
  switch (status) {
    case 'draft':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    case 'scheduled':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
    case 'in_progress':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300'
    case 'done':
      return 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
    case 'error':
      return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  }
}

onMounted(fetchMailings)
</script>

