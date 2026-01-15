<template>
  <div class="max-w-6xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Управление меню</h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Синхронизация меню по группам (как в админ-панели)
        </p>
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

      <div class="p-6">
        <!-- Step 1: Fetch Structure -->
        <div class="mb-8">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Шаг 1: Получить структуру меню из iiko
          </h3>
          <button
            @click="handleFetchMenuStructure"
            :disabled="loading"
            class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700
                   text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            <Icon
              :icon="loading && step === 1 ? 'mdi:loading' : 'mdi:refresh'"
              :class="{ 'animate-spin': loading && step === 1 }"
              class="w-5 h-5"
            />
            Загрузить структуру
          </button>
        </div>

        <!-- Step 2: Select Groups -->
        <div v-if="menuGroups && menuGroups.length > 0">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Шаг 2: Выберите группы для загрузки
            </h3>
            <button 
              @click="toggleSelectAll"
              class="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
            >
              {{ isAllSelected ? 'Снять выделение' : 'Выбрать все' }}
            </button>
          </div>

          <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="group in menuGroups"
              :key="group.id"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-3
                     hover:border-blue-500 dark:hover:border-blue-400 transition-colors cursor-pointer"
              :class="{
                'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20': isSelected(group.id)
              }"
              @click="toggleGroup(group.id)"
            >
              <div class="flex items-start gap-3">
                <div class="pt-0.5">
                   <Icon 
                     :icon="isSelected(group.id) ? 'mdi:checkbox-marked' : 'mdi:checkbox-blank-outline'"
                     class="w-5 h-5"
                     :class="isSelected(group.id) ? 'text-blue-600' : 'text-gray-400'"
                   />
                </div>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white leading-tight">
                    {{ group.name }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Подкатегорий: {{ group.childrenCount || 0 }}
                  </p>
                  <p class="text-xs text-gray-400 mt-0.5">ID: {{ group.id.slice(0, 8) }}...</p>
                </div>
              </div>
            </div>
          </div>

          <button
            @click="handleLoadSelected"
            :disabled="selectedGroups.length === 0 || loading"
            class="mt-6 flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-700
                   text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon
              :icon="loading && step === 2 ? 'mdi:loading' : 'mdi:download'"
              :class="{ 'animate-spin': loading && step === 2 }"
              class="w-5 h-5"
            />
            Загрузить выбранные ({{ selectedGroups.length }})
          </button>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="!loading && step === 0 && (!menuGroups || menuGroups.length === 0)"
          class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
        >
          <Icon icon="mdi:food-off" class="w-16 h-16 mb-4" />
          <p class="text-lg font-medium">Структура меню не загружена</p>
          <p class="text-sm">Нажмите кнопку выше для получения списка групп</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading && step === 1" class="flex justify-center py-12">
            <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const selectedGroups = ref([])
const successMessage = ref('')
const error = ref(null)
const step = ref(0)
const loading = computed(() => organizationStore.loading)
const menuGroups = computed(() => organizationStore.menuGroups || [])

const isSelected = (id) => selectedGroups.value.includes(id)
const isAllSelected = computed(() => menuGroups.value.length > 0 && selectedGroups.value.length === menuGroups.value.length)

const toggleGroup = (id) => {
  if (isSelected(id)) {
    selectedGroups.value = selectedGroups.value.filter(g => g !== id)
  } else {
    selectedGroups.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedGroups.value = []
  } else {
    selectedGroups.value = menuGroups.value.map(g => g.id)
  }
}

const handleFetchMenuStructure = async () => {
  error.value = null
  successMessage.value = ''
  step.value = 1
  selectedGroups.value = [] // Reset selection on new fetch

  try {
    await organizationStore.fetchMenuGroups()
    successMessage.value = 'Структура меню успешно получена'
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось получить структуру меню'
  } finally {
    step.value = 0
  }
}

const handleLoadSelected = async () => {
  if (selectedGroups.value.length === 0) return

  error.value = null
  successMessage.value = ''
  step.value = 2

  try {
    const result = await organizationStore.loadMenuGroups(selectedGroups.value)
    successMessage.value = result.message || 'Меню успешно синхронизировано'
    // Clear selection? Maybe keep it.
    // selectedGroups.value = []
    setTimeout(() => { successMessage.value = '' }, 5000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось загрузить меню'
  } finally {
    step.value = 0
  }
}
</script>
