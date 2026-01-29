<template>
  <div class="max-w-6xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Терминалы</h2>
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
      <div v-if="loading && terminals.length === 0" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && terminals.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:tablet-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Терминалы не найдены</p>
        <p class="text-sm">Нажмите "Загрузить из IIKO" для импорта терминалов</p>
      </div>

      <!-- Terminals Table -->
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
                Интервал обновления (мин)
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Рабочее время
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Расчет доставки
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Ссылка на Instagram
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="terminal in terminals"
              :key="terminal.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:tablet" class="w-5 h-5 text-blue-600" />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ terminal.name }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-500 dark:text-gray-400 font-mono">
                  {{ terminal.iiko_terminal_id }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <input
                  v-model.number="terminal.stop_list_interval_min"
                  @blur="updateTerminalInterval(terminal)"
                  type="number"
                  min="1"
                  class="w-20 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-gray-500 dark:text-gray-400">Начало</label>
                    <input
                      :value="getWorkingHoursValue(terminal, 'start')"
                      @input="(e) => setWorkingHoursValue(terminal, 'start', e.target.value)"
                      @blur="updateWorkingHours(terminal)"
                      type="time"
                      class="w-24 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded 
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <span class="text-gray-400 mt-5">-</span>
                  <div class="flex flex-col gap-1">
                    <label class="text-xs text-gray-500 dark:text-gray-400">Конец</label>
                    <input
                      :value="getWorkingHoursValue(terminal, 'end')"
                      @input="(e) => setWorkingHoursValue(terminal, 'end', e.target.value)"
                      @blur="updateWorkingHours(terminal)"
                      type="time"
                      class="w-24 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded 
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      terminal.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                    ]"
                  >
                    {{ terminal.is_active ? 'Активен' : 'Неактивен' }}
                  </span>
                  <button
                    @click="handleToggleActive(terminal)"
                    :disabled="togglingTerminal === terminal.id"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    :class="terminal.is_active ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'"
                  >
                    <span
                      class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                      :class="terminal.is_active ? 'translate-x-6' : 'translate-x-1'"
                    />
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      (terminal.is_delivery_calculation_apply ?? false)
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                    ]"
                  >
                    {{ (terminal.is_delivery_calculation_apply ?? false) ? 'Включен' : 'Выключен' }}
                  </span>
                  <button
                    @click="toggleDeliveryCalculation(terminal)"
                    :disabled="togglingDeliveryCalculation === terminal.id"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    :class="(terminal.is_delivery_calculation_apply ?? false) ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'"
                  >
                    <span
                      class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                      :class="(terminal.is_delivery_calculation_apply ?? false) ? 'translate-x-6' : 'translate-x-1'"
                    />
                  </button>
                </div>
              </td>
              <td class="px-6 py-4">
                <input
                  v-model="terminal.instagram_link"
                  @blur="updateTerminalInstagram(terminal)"
                  type="url"
                  placeholder="https://instagram.com/..."
                  class="w-full min-w-[180px] px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="syncStopList(terminal)"
                  :disabled="syncingStopList === terminal.id"
                  class="flex items-center gap-2 px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700
                         text-white font-medium rounded-lg transition-colors disabled:opacity-50"
                >
                  <Icon
                    :icon="syncingStopList === terminal.id ? 'mdi:loading' : 'mdi:refresh'"
                    :class="{ 'animate-spin': syncingStopList === terminal.id }"
                    class="w-4 h-4"
                  />
                  Обновить стоп-лист
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div
      v-if="showConfirmModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="closeConfirmModal"
    >
      <div class="bg-white dark:bg-gray-800 w-full max-w-md rounded-2xl shadow-2xl">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            Подтверждение действия
          </h3>
        </div>
        
        <div class="p-6">
          <p class="text-gray-700 dark:text-gray-300 mb-6">
            {{ confirmModalMessage }}
          </p>
          
          <div class="flex gap-3 justify-end">
            <button
              @click="closeConfirmModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
            >
              Отмена
            </button>
            <button
              @click="confirmToggleActive"
              :disabled="togglingTerminal !== null"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {{ togglingTerminal !== null ? 'Обработка...' : 'Да' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'
import organizationService from '@/services/organization.service'

const organizationStore = useOrganizationStore()

const successMessage = ref('')
const error = ref(null)
const syncingStopList = ref(null)
const showConfirmModal = ref(false)
const terminalToToggle = ref(null)
const togglingTerminal = ref(null)
const confirmModalMessage = ref('')
const togglingDeliveryCalculation = ref(null)

const loading = computed(() => organizationStore.loading)
const terminals = computed(() => organizationStore.terminals || [])

onMounted(async () => {
  await loadTerminals()
})

const loadTerminals = async () => {
  error.value = null
  try {
    await organizationStore.fetchTerminals()
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось загрузить терминалы'
  }
}

const handleLoadFromIiko = async () => {
  error.value = null
  successMessage.value = ''

  try {
    const result = await organizationStore.loadTerminalsFromIiko()
    successMessage.value = result.message || 'Терминалы успешно загружены из IIKO'

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось загрузить терминалы из IIKO'
  }
}

// Хранилище временных значений рабочего времени для каждого терминала
const workingHoursTemp = ref({})

// Получение значения рабочего времени (из временного хранилища или из терминала)
const getWorkingHoursValue = (terminal, field) => {
  // Инициализируем, если еще нет
  if (!workingHoursTemp.value[terminal.id]) {
    workingHoursTemp.value[terminal.id] = {
      start: terminal.working_hours?.start || '',
      end: terminal.working_hours?.end || ''
    }
  }
  return workingHoursTemp.value[terminal.id][field] || ''
}

// Установка временного значения рабочего времени
const setWorkingHoursValue = (terminal, field, value) => {
  if (!workingHoursTemp.value[terminal.id]) {
    workingHoursTemp.value[terminal.id] = {
      start: terminal.working_hours?.start || '',
      end: terminal.working_hours?.end || ''
    }
  }
  workingHoursTemp.value[terminal.id][field] = value
}

const updateWorkingHours = async (terminal) => {
  // Инициализируем временные значения, если их еще нет
  if (!workingHoursTemp.value[terminal.id]) {
    workingHoursTemp.value[terminal.id] = {
      start: terminal.working_hours?.start || '',
      end: terminal.working_hours?.end || ''
    }
  }
  
  const tempHours = workingHoursTemp.value[terminal.id]
  
  // Сохраняем только если указаны оба поля (начало и конец)
  if (!tempHours.start || !tempHours.end) {
    return // Не сохраняем, если не заполнены оба поля
  }
  
  // Проверяем, изменились ли значения
  const currentStart = terminal.working_hours?.start || ''
  const currentEnd = terminal.working_hours?.end || ''
  
  if (tempHours.start === currentStart && tempHours.end === currentEnd) {
    return // Значения не изменились, не нужно сохранять
  }

  try {
    error.value = null
    
    const updatedWorkingHours = {
      start: tempHours.start,
      end: tempHours.end
    }
    
    await organizationService.updateTerminal(terminal.id, {
      working_hours: updatedWorkingHours
    })
    
    // Обновляем локальное состояние терминала
    terminal.working_hours = updatedWorkingHours
    
    successMessage.value = 'Рабочее время сохранено'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось обновить рабочее время'
    // Восстанавливаем исходные значения при ошибке
    workingHoursTemp.value[terminal.id] = {
      start: terminal.working_hours?.start || '',
      end: terminal.working_hours?.end || ''
    }
  }
}

const updateTerminalInterval = async (terminal) => {
  if (!terminal.stop_list_interval_min || terminal.stop_list_interval_min < 1) {
    error.value = 'Интервал должен быть не менее 1 минуты'
    return
  }

  try {
    await organizationService.updateTerminal(terminal.id, {
      stop_list_interval_min: terminal.stop_list_interval_min
    })
    successMessage.value = 'Интервал обновления сохранен'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось обновить интервал'
  }
}

const updateTerminalInstagram = async (terminal) => {
  try {
    error.value = null
    await organizationService.updateTerminal(terminal.id, {
      instagram_link: terminal.instagram_link || null
    })
    successMessage.value = 'Ссылка на Instagram сохранена'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось сохранить ссылку на Instagram'
  }
}

const syncStopList = async (terminal) => {
  syncingStopList.value = terminal.id
  error.value = null
  successMessage.value = ''

  try {
    const result = await organizationService.syncTerminalStopList(terminal.id)
    successMessage.value = result.message || `Стоп-лист обновлен: ${result.data?.updated_count || 0} позиций`
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось синхронизировать стоп-лист'
  } finally {
    syncingStopList.value = null
  }
}

const handleToggleActive = (terminal) => {
  terminalToToggle.value = terminal
  if (terminal.is_active) {
    confirmModalMessage.value = `Вы уверены, что хотите деактивировать терминал "${terminal.name || terminal.terminal_group_name}"? Терминал останется в списке, но не будет доступен в Telegram mini app.`
  } else {
    confirmModalMessage.value = `Вы уверены, что хотите активировать терминал "${terminal.name || terminal.terminal_group_name}"?`
  }
  showConfirmModal.value = true
}

const closeConfirmModal = () => {
  showConfirmModal.value = false
  terminalToToggle.value = null
  confirmModalMessage.value = ''
}

const confirmToggleActive = async () => {
  if (!terminalToToggle.value) return

  togglingTerminal.value = terminalToToggle.value.id
  error.value = null
  successMessage.value = ''

  try {
    const result = await organizationService.toggleTerminalActive(terminalToToggle.value.id)
    
    // Обновляем локальное состояние терминала
    const terminal = terminals.value.find(t => t.id === terminalToToggle.value.id)
    if (terminal) {
      terminal.is_active = result.data.is_active
    }
    
    successMessage.value = result.message || (result.data.is_active ? 'Терминал активирован' : 'Терминал деактивирован')
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
    closeConfirmModal()
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось изменить статус терминала'
  } finally {
    togglingTerminal.value = null
  }
}

const toggleDeliveryCalculation = async (terminal) => {
  togglingDeliveryCalculation.value = terminal.id
  error.value = null
  successMessage.value = ''

  try {
    const currentValue = terminal.is_delivery_calculation_apply ?? false
    const newValue = !currentValue
    
    await organizationService.updateTerminal(terminal.id, {
      is_delivery_calculation_apply: newValue
    })
    
    // Обновляем локальное состояние терминала
    terminal.is_delivery_calculation_apply = newValue
    
    successMessage.value = newValue 
      ? 'Расчет стоимости доставки включен' 
      : 'Расчет стоимости доставки выключен'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось изменить настройку расчета доставки'
  } finally {
    togglingDeliveryCalculation.value = null
  }
}
</script>
