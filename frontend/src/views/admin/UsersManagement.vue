<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 pb-20">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-6">
        <button @click="$router.back()" class="p-2 -ml-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 w-10 h-10 flex items-center justify-center bg-white dark:bg-gray-800 shadow-sm transition-colors">
            <svg class="w-6 h-6 text-gray-900 dark:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
        </button>
        <h1 class="text-2xl font-bold flex-1 text-gray-900 dark:text-white">Пользователи</h1>
        <button 
          @click="showCreateModal = true"
          class="w-10 h-10 bg-primary-600 text-white rounded-lg flex items-center justify-center shadow-lg active:scale-95 transition-transform"
        >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
        </button>
    </div>

    <!-- Stats -->
    <div class="flex gap-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        <button 
          v-for="role in rolesFilter" 
          :key="role.id"
          @click="activeFilter = role.id"
          class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all"
          :class="activeFilter === role.id ? 'bg-primary-600 text-white shadow-md' : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-100 dark:border-gray-700'"
        >
            {{ role.name }}
        </button>
    </div>

    <!-- Search -->
    <div class="relative mb-6">
        <input 
            v-model="searchQuery"
            type="text" 
            placeholder="Поиск по имени или телефону" 
            class="w-full pl-10 pr-4 py-3 rounded-2xl border-none shadow-sm focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400"
        >
        <svg class="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-12">
        <div class="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mb-4"></div>
        <p class="text-gray-500">Загрузка пользователей...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="totalUsers === 0" class="text-center py-12 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-dashed border-gray-200 dark:border-gray-700">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">Пользователи не найдены</h3>
        <p class="text-sm text-gray-500">Попробуйте изменить параметры поиска</p>
    </div>

    <!-- Users Table -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900/40">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Имя</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Роль</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Telegram ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Телефон</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Терминал</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Подписка</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Адрес подтвержден</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Действие</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="user in paginatedUsers"
              :key="user.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/40"
            >
              <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-bold">
                    {{ (user.first_name || user.username || 'U')[0].toUpperCase() }}
                  </div>
                  <div>
                    <div class="leading-tight">{{ user.full_name || user.username }}</div>
                    <div v-if="user.updated_at" class="text-[11px] text-gray-400">
                      Обновлён: {{ formatUpdatedAt(user.updated_at) }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-200">
                <span
                  class="text-[11px] px-2 py-1 rounded-md font-bold uppercase"
                  :class="{
                    'bg-blue-100 text-blue-700': user.role_name === 'org_admin',
                    'bg-green-100 text-green-700': user.role_name === 'customer',
                    'bg-purple-100 text-purple-700': user.role_name === 'superadmin'
                  }"
                >
                  {{ user.role_display }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                {{ user.telegram_id || '-' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                {{ user.phone || '-' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                {{ formatUserTerminals(user) }}
              </td>
              <td class="px-4 py-3 text-sm">
                <span
                  class="text-[11px] px-2 py-1 rounded-md font-semibold"
                  :class="{
                    'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400': user.is_bot_subscribed === true,
                    'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400': user.is_bot_subscribed === false,
                    'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400': user.is_bot_subscribed == null
                  }"
                  :title="user.is_bot_subscribed === true && user.chat_id ? `chat_id: ${user.chat_id}` : ''"
                >
                  {{ user.is_bot_subscribed === true ? 'Подписан' : user.is_bot_subscribed === false ? 'Отказ' : 'Не выбрано' }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                <span v-if="isAnyAddressVerified(user)" class="text-green-600 font-semibold">Да</span>
                <span v-else class="text-gray-400">Нет</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  @click="editUser(user)"
                  class="w-9 h-9 inline-flex items-center justify-center text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  title="Редактировать"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                  </svg>
                </button>
              </td>
            </tr>
            <tr v-if="paginatedUsers.length === 0">
              <td colspan="8" class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                Пользователи не найдены
              </td>
            </tr>
          </tbody>
        </table>
      </div>

        <!-- Pagination -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4">
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
                  ? 'bg-primary-600 text-white border-primary-600'
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

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm transition-opacity">
        <div class="bg-white dark:bg-gray-800 w-full max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden transform transition-all animate-slide-up sm:animate-scale-in">
            <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ editingUser ? 'Редактировать' : 'Новый клиент' }}
                </h3>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-600 p-2">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <div class="p-6 overflow-y-auto">
                <form @submit.prevent="saveUser" class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="col-span-1">
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Имя</label>
                            <input v-model="form.first_name" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white" placeholder="Иван">
                        </div>
                        <div class="col-span-1">
                            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Фамилия</label>
                            <input v-model="form.last_name" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white" placeholder="Иванов">
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Логин / Username</label>
                        <input v-model="form.username" type="text" required class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white" placeholder="ivanov_123">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Телефон</label>
                        <input v-model="form.phone" type="tel" class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white" placeholder="+7 (___) ___ __ __">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Telegram ID (если есть)</label>
                        <input v-model="form.telegram_id" type="number" class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white" placeholder="123456789">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Роль</label>
                        <select v-model="form.role" class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white appearance-none">
                            <option v-for="role in allRoles" :key="role.id" :value="role.id">
                                {{ role.role_name === 'customer' ? 'Клиент' : 'Администратор' }}
                            </option>
                        </select>
                    </div>

                    <!-- Terminal Selection -->
                    <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Терминалы</label>
                        <div class="space-y-2 max-h-48 overflow-y-auto p-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                            <div v-if="availableTerminals.length === 0" class="text-xs text-gray-500 text-center py-2">
                                Нет доступных терминалов
                            </div>
                            <label v-for="terminal in availableTerminals" :key="terminal.id" class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors">
                                <div class="relative flex items-center">
                                    <input 
                                        type="checkbox" 
                                        :value="terminal.id" 
                                        v-model="form.terminals"
                                        class="peer w-5 h-5 rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500 dark:bg-gray-700 transition duration-150 ease-in-out"
                                    >
                                </div>
                                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                    {{ terminal.name }}
                                </span>
                            </label>
                        </div>
                        <p class="text-[10px] text-gray-400 mt-1 pl-1">Выберите один или несколько терминалов</p>
                    </div>

                    <div v-if="modalError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-xl">
                        {{ modalError }}
                    </div>

                    <!-- Delivery Addresses (read-only + coordinates tools) -->
                    <div v-if="editingUser" class="pt-4 border-t border-gray-100 dark:border-gray-700">
                      <h4 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
                        Адреса доставки
                      </h4>
                      <div v-if="addressRows.length === 0" class="text-sm text-gray-500 dark:text-gray-400">
                        Адресов нет
                      </div>
                      <div v-else class="space-y-3">
                        <div
                          v-for="row in addressRows"
                          :key="row.id"
                          class="p-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
                        >
                          <div class="flex items-start justify-between gap-3">
                            <div class="flex-1">
                              <div class="text-sm font-semibold text-gray-900 dark:text-white">
                                {{ row.full_address || '—' }}
                              </div>
                              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                <span v-if="row.is_verified">✅ Подтвержден</span>
                                <span v-else>⚠️ Не подтвержден</span>
                              </div>
                            </div>
                            <button
                              type="button"
                              class="text-xs px-3 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
                              :disabled="row.geocoding"
                              @click="runGeocoder(row)"
                            >
                              {{ row.geocoding ? 'Геокодер...' : 'Запустить геокодер' }}
                            </button>
                          </div>

                          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3">
                            <div>
                              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Широта</label>
                              <input
                                v-model="row.latitude"
                                type="text"
                                inputmode="decimal"
                                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                                placeholder="43.1234567"
                              >
                            </div>
                            <div>
                              <label class="block text-[10px] font-bold text-gray-500 uppercase mb-1">Долгота</label>
                              <input
                                v-model="row.longitude"
                                type="text"
                                inputmode="decimal"
                                class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                                placeholder="76.1234567"
                              >
                            </div>
                            <div class="flex items-end">
                              <button
                                type="button"
                                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-semibold text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-60"
                                :disabled="row.saving"
                                @click="saveAddressCoordinates(row)"
                              >
                                {{ row.saving ? 'Сохранение...' : 'Сохранить' }}
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="pt-4">
                        <button 
                          type="submit" 
                          :disabled="modalLoading"
                          class="w-full bg-primary-600 text-white py-4 rounded-xl font-bold shadow-lg hover:bg-primary-700 active:scale-95 transition-all disabled:opacity-50"
                        >
                            {{ modalLoading ? 'Сохранение...' : (editingUser ? 'Сохранить изменения' : 'Создать пользователя') }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import usersService from '@/services/users.service'
import { useOrganizationStore } from '@/stores/organization'
import deliveryAddressService from '@/services/delivery-address.service'
import { useNotificationStore } from '@/stores/notifications'

const loading = ref(true)
const users = ref([]) // текущая страница
const totalCount = ref(0)
const allRoles = ref([])
const organizationStore = useOrganizationStore()
const availableTerminals = computed(() => organizationStore.terminals)
const activeFilter = ref('all')
const searchQuery = ref('')

const showCreateModal = ref(false)
const editingUser = ref(null)
const modalLoading = ref(false)
const modalError = ref('')
const notificationStore = useNotificationStore()

const addressRows = ref([]) // [{ id, full_address, latitude, longitude, is_verified, saving, geocoding }]

const rolesFilter = [
    { id: 'all', name: 'Все' },
    { id: 'customer', name: 'Клиенты' },
    { id: 'org_admin', name: 'Админы' }
]

const form = reactive({
    username: '',
    first_name: '',
    last_name: '',
    phone: '',
    telegram_id: '',
    role: null,
    terminals: []
})

function formatUpdatedAt(isoString) {
    if (!isoString) return '-'
    try {
        const d = new Date(isoString)
        return d.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    } catch {
        return isoString
    }
}

const PAGINATION_WINDOW = 12
const PAGINATION_LAST = 3

const currentPage = ref(1)
const perPage = ref(20)
const paginationWindowStart = ref(1)

const totalUsers = computed(() => totalCount.value)
const totalPages = computed(() => Math.max(1, Math.ceil((totalCount.value || 0) / (perPage.value || 20))))
const paginatedUsers = computed(() => users.value)

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

function getRoleIdByRoleName(roleName) {
  const role = (allRoles.value || []).find(r => r.role_name === roleName)
  return role?.id ?? null
}

async function fetchUsersPage() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: perPage.value,
    }

    if (searchQuery.value?.trim()) {
      params.search = searchQuery.value.trim()
    }

    if (activeFilter.value !== 'all') {
      const roleId = getRoleIdByRoleName(activeFilter.value)
      if (roleId) params.role = roleId
    }

    const data = await usersService.getUsers(params)
    users.value = Array.isArray(data) ? data : (data.results || [])
    totalCount.value = data?.count ?? users.value.length
  } catch (err) {
    console.error('Fetch users error:', err)
    users.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

async function fetchData() {
    loading.value = true
    try {
        const [rolesData] = await Promise.all([
            usersService.getRoles(),
            organizationStore.fetchTerminals()
        ])
        
        allRoles.value = Array.isArray(rolesData) ? rolesData : (rolesData.results || [])
        
        // По умолчанию ставим роль "клиент" для формы
        const customerRole = allRoles.value.find(r => r.role_name === 'customer')
        if (customerRole) form.role = customerRole.id

        await fetchUsersPage()
    } catch (err) {
        console.error('Fetch error:', err)
    } finally {
        // fetchUsersPage уже снимает loading, но оставим на всякий случай
        loading.value = false
    }
}

function closeModal() {
    showCreateModal.value = false
    editingUser.value = null
    modalError.value = ''
    resetForm()
}

function resetForm() {
    form.username = ''
    form.first_name = ''
    form.last_name = ''
    form.phone = ''
    form.telegram_id = ''
    form.terminals = []
    const customerRole = allRoles.value.find(r => r.role_name === 'customer')
    if (customerRole) form.role = customerRole.id
}

function editUser(user) {
    editingUser.value = user
    form.username = user.username
    form.first_name = user.first_name || ''
    form.last_name = user.last_name || ''
    form.phone = user.phone || ''
    form.telegram_id = user.telegram_id || ''
    form.role = user.role
    // Если у пользователя есть терминалы, заполняем форму.
    // Предполагаем, что с бэкенда приходит массив ID или объектов терминалов
    form.terminals = user.terminals 
        ? user.terminals.map(t => typeof t === 'object' ? t.id : t) 
        : []
    showCreateModal.value = true

    // Адреса (для модалки)
    const raw = Array.isArray(user.addresses) ? user.addresses : []
    addressRows.value = raw.map(a => ({
      id: a.id,
      full_address: a.full_address || '',
      latitude: a.latitude ?? '',
      longitude: a.longitude ?? '',
      is_verified: !!a.is_verified,
      saving: false,
      geocoding: false,
    }))
}

function formatUserTerminals(user) {
  const terms = Array.isArray(user?.terminals) ? user.terminals : []
  if (!terms.length) return '-'
  const names = terms.map(t => (typeof t === 'object' ? (t.name || t.terminal_group_name || t.id) : t)).filter(Boolean)
  return names.join(', ')
}

function isAnyAddressVerified(user) {
  const addrs = Array.isArray(user?.addresses) ? user.addresses : []
  return addrs.some(a => a?.is_verified)
}

async function saveAddressCoordinates(row) {
  if (!row?.id) return
  row.saving = true
  try {
    const updated = await deliveryAddressService.updateCoordinates(row.id, row.latitude, row.longitude)
    row.latitude = updated.latitude ?? row.latitude
    row.longitude = updated.longitude ?? row.longitude
    row.is_verified = !!updated.is_verified
    notificationStore.show('Координаты сохранены')
    // обновим пользователя из списка (локально), чтобы колонка "подтвержден" обновилась
    if (editingUser.value?.addresses) {
      const idx = editingUser.value.addresses.findIndex(a => a.id === row.id)
      if (idx >= 0) editingUser.value.addresses[idx] = updated
    }
  } catch (err) {
    const msg = err.response?.data?.detail || 'Не удалось сохранить координаты'
    notificationStore.show(msg, 4000)
  } finally {
    row.saving = false
  }
}

async function runGeocoder(row) {
  if (!row?.id) return
  row.geocoding = true
  try {
    // Для админки просим синхронный ответ с ошибкой (если будет)
    const updated = await deliveryAddressService.geocodeAddress(row.id, { sync: true })
    // backend может вернуть либо объект адреса, либо {status,message}
    if (updated?.id) {
      row.latitude = updated.latitude ?? row.latitude
      row.longitude = updated.longitude ?? row.longitude
      row.is_verified = !!updated.is_verified
      notificationStore.show('Геокодирование выполнено')
      if (editingUser.value?.addresses) {
        const idx = editingUser.value.addresses.findIndex(a => a.id === row.id)
        if (idx >= 0) editingUser.value.addresses[idx] = updated
      }
    } else {
      notificationStore.show(updated?.message || 'Геокодирование запущено', 3000)
    }
  } catch (err) {
    const msg = err.response?.data?.detail || 'Ошибка геокодера'
    notificationStore.show(msg, 5000)
  } finally {
    row.geocoding = false
  }
}

async function saveUser() {
    modalLoading.value = true
    modalError.value = ''
    
    try {
        const payload = { ...form }
        if (!payload.telegram_id) delete payload.telegram_id
        
        if (editingUser.value) {
            await usersService.updateUser(editingUser.value.id, payload)
        } else {
            await usersService.createUser(payload)
        }
        
        await fetchUsersPage()
        closeModal()
    } catch (err) {
        console.error('Save error:', err)
        modalError.value = err.response?.data?.message || err.response?.data?.error || 'Произошла ошибка при сохранении'
        
        // Handle field-specific errors if any
        if (err.response?.data) {
           const details = Object.entries(err.response.data)
             .map(([key, val]) => `${key}: ${val}`)
             .join('\n')
           if (details) modalError.value = details
        }
    } finally {
        modalLoading.value = false
    }
}

onMounted(fetchData)

let searchDebounceTimer = null
watch(searchQuery, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    paginationWindowStart.value = 1
    fetchUsersPage()
  }, 400)
})

watch(activeFilter, async () => {
  currentPage.value = 1
  paginationWindowStart.value = 1
  await fetchUsersPage()
})

watch(perPage, async () => {
  currentPage.value = 1
  paginationWindowStart.value = 1
  await fetchUsersPage()
})

watch(currentPage, async () => {
  await fetchUsersPage()
})

watch(totalPages, (newTotal) => {
  if (newTotal <= 15) paginationWindowStart.value = 1
  else paginationWindowStart.value = Math.min(paginationWindowStart.value, newTotal - 14)
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
    display: none;
}
.scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

@keyframes slide-up {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
}

@keyframes scale-in {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.animate-slide-up {
    animation: slide-up 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-scale-in {
    animation: scale-in 0.2s ease-out;
}
</style>

