<template>
  <div class="min-h-screen bg-gray-50 p-4 pb-20">
    <div class="max-w-md mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          Выберите точку продажи
        </h1>
        <p class="text-gray-600 text-sm">
          Выберите точку продажи заведения для заказа
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full"></div>
      </div>

      <!-- Error message -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <!-- Terminals List -->
      <div v-else-if="terminals.length > 0" class="space-y-3">
        <button
          v-for="terminal in terminals"
          :key="terminal.id"
          @click="selectTerminal(terminal)"
          :disabled="saving"
          class="w-full bg-white rounded-2xl p-6 shadow-sm border-2 border-gray-200 hover:border-primary-500 
                 transition-all active:scale-95 flex items-center gap-4 disabled:opacity-50"
        >
          <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div class="flex-1 text-left">
            <h3 class="font-semibold text-gray-900 mb-1">
              {{ terminal.name || terminal.terminal_group_name }}
            </h3>
            <p v-if="terminal.city" class="text-sm text-gray-500">
              {{ terminal.city }}
            </p>
          </div>
          <svg v-if="!saving" class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          <div v-else class="animate-spin w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full"></div>
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && terminals.length === 0" class="bg-white rounded-2xl p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          Точки продажи не найдены
        </h3>
        <p class="text-gray-600 text-sm mb-4">
          В вашем заведении пока нет доступных точек продажи
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrganizationStore } from '@/stores/organization'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const organizationStore = useOrganizationStore()
const authStore = useAuthStore()

const terminals = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadTerminals()
})

async function loadTerminals() {
  loading.value = true
  error.value = null

  try {
    // Загружаем терминалы организации пользователя
    const data = await organizationStore.fetchTerminals()
    
    // Фильтруем только активные терминалы
    terminals.value = (data || []).filter(t => t.is_active !== false)
    
    // Если терминал один - автоматически выбираем его
    if (terminals.value.length === 1) {
      console.log('Only one terminal found, auto-selecting...')
      await selectTerminal(terminals.value[0])
      return
    }
    
    // Если терминалов нет - показываем сообщение
    if (terminals.value.length === 0) {
      error.value = 'В вашей организации нет доступных терминалов'
    }
  } catch (err) {
    console.error('Load terminals error:', err)
    error.value = organizationStore.error || 'Не удалось загрузить терминалы'
  } finally {
    loading.value = false
  }
}

async function selectTerminal(terminal) {
  saving.value = true
  error.value = null

  try {
    // Сохраняем выбранный терминал в пользователе
    // В B2C flow терминалы привязываются к пользователю через ManyToMany
    // Обновляем пользователя через API, добавляя выбранный терминал
    const user = authStore.user
    
    if (user) {
      // Получаем текущие терминалы пользователя (если есть)
      const currentTerminals = user.terminals || []
      const terminalIds = currentTerminals.map(t => typeof t === 'object' ? t.id || t.terminal_id : t)
      
      // Добавляем выбранный терминал, если его еще нет
      if (!terminalIds.includes(terminal.id || terminal.terminal_id)) {
        terminalIds.push(terminal.id || terminal.terminal_id)
      }
      
      // Обновляем пользователя через API
      const usersService = (await import('@/services/users.service')).default
      await usersService.updateProfile({ 
        terminals: terminalIds 
      })
      
      // Перезагружаем данные пользователя для получения обновленных терминалов
      await authStore.fetchCurrentUser()
    }
    
    // Переходим к меню
    router.push('/menu')
  } catch (err) {
    console.error('Select terminal error:', err)
    error.value = err.response?.data?.detail || err.response?.data?.error || 'Не удалось выбрать терминал'
    saving.value = false
  }
}
</script>
