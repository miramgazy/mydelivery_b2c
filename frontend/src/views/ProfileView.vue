<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 flex flex-col items-center border-b border-gray-200 dark:border-gray-700">
        <div class="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-4 text-3xl">
            👋
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ user?.full_name || 'Пользователь' }}</h1>
        <p class="text-gray-500">{{ user?.phone || 'Телефон не указан' }}</p>
    </div>

    <!-- Actions -->
    <div class="p-4 space-y-4">
        <!-- Profile Data -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg">
                Личные данные
            </div>
            <div class="p-4 space-y-4">
                <div>
                     <label class="block text-sm text-gray-500 mb-1">Имя</label>
                     <div class="font-medium">{{ user?.first_name }}</div>
                </div>
                <div>
                     <label class="block text-sm text-gray-500 mb-1">Фамилия</label>
                     <div class="font-medium">{{ user?.last_name || '-' }}</div>
                </div>
                 <div>
                     <label class="block text-sm text-gray-500 mb-1">Telegram ID</label>
                     <div class="font-mono text-sm bg-gray-100 dark:bg-gray-700 p-2 rounded">{{ user?.telegram_id }}</div>
                </div>
            </div>
        </div>

        <!-- Terminal Selection -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg flex justify-between items-center">
                <span>Точка продажи</span>
            </div>
            <div class="p-4">
                <div v-if="currentTerminal" class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900 dark:text-white mb-1">
                            {{ terminalDisplayName(currentTerminal) }}
                        </div>
                        <div v-if="currentTerminal.city_name || currentTerminal.city" class="text-sm text-gray-500">
                            {{ currentTerminal.city_name || currentTerminal.city }}
                        </div>
                    </div>
                    <button
                        @click="showTerminalModal = true"
                        class="ml-4 px-4 py-2 text-primary-600 font-semibold hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                    >
                        Изменить
                    </button>
                </div>
                <div v-else class="text-center text-gray-500 text-sm py-2">
                    <p class="mb-2">Точка продажи не выбрана</p>
                    <button
                        @click="showTerminalModal = true"
                        class="text-primary-600 font-semibold hover:underline"
                    >
                        Выбрать точку продажи
                    </button>
                </div>
            </div>
        </div>

        <!-- Addresses (Placeholder for now) -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
             <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg flex justify-between items-center">
                <span>Мои адреса</span>
                <button
                  @click="goToAddresses"
                  class="text-primary-600 text-sm font-semibold hover:underline"
                >
                  Управлять
                </button>
            </div>
            <div v-if="user?.addresses?.length" class="p-4 space-y-2">
              <div
                v-for="addr in user.addresses.slice(0, 3)"
                :key="addr.id"
                class="p-3 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex items-center justify-between gap-3"
              >
                <div class="text-sm">
                  <div class="font-medium text-gray-900 dark:text-white">
                    {{ addr.full_address }}
                  </div>
                  <div v-if="addr.is_default" class="text-xs text-primary-600 font-semibold">Основной</div>
                </div>
              </div>
              <button
                @click="goToAddresses"
                class="w-full py-2 rounded-xl border-2 border-primary-200 text-primary-600 font-semibold hover:bg-primary-50 transition-colors"
              >
                Открыть список адресов
              </button>
            </div>
            <div v-else class="p-4 text-center text-gray-500 text-sm italic space-y-2">
              <div>Адресов пока нет</div>
              <button
                @click="goToAddresses"
                class="text-primary-600 font-semibold underline"
              >
                Добавить адрес
              </button>
            </div>
        </div>

         <!-- About -->
        <div class="bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-sm">
             <div class="p-4 border-b border-gray-100 dark:border-gray-700 font-semibold text-lg">
                О приложении
            </div>
            <div class="p-4 space-y-2">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Версия</span>
                    <span>1.0.0</span>
                </div>
                 <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Организация</span>
                    <span>{{ user?.organization_name || '-' }}</span>
                </div>
            </div>
        </div>
        
        <!-- Logout -->
        <button 
            @click="logout"
            class="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
            Выйти
        </button>
    </div>

    <!-- Terminal Selection Modal -->
    <div v-if="showTerminalModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div 
            class="fixed inset-0 bg-black/60 transition-opacity"
            @click="showTerminalModal = false"
        ></div>

        <!-- Modal -->
        <div class="relative w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden flex flex-col max-h-[80vh]">
            <!-- Header -->
            <div class="p-6 border-b border-gray-100 dark:border-gray-700">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                        Выберите точку продажи
                    </h2>
                    <button
                        @click="showTerminalModal = false"
                        class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Content -->
            <div class="flex-1 overflow-y-auto p-4">
                <!-- Loading -->
                <div v-if="loadingTerminals" class="flex items-center justify-center py-12">
                    <div class="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full"></div>
                </div>

                <!-- Error -->
                <div v-else-if="terminalError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
                    {{ terminalError }}
                </div>

                <!-- Terminals List -->
                <div v-else-if="availableTerminals.length > 0" class="space-y-2">
                    <button
                        v-for="terminal in availableTerminals"
                        :key="terminal.id || terminal.terminal_id"
                        @click="selectTerminal(terminal)"
                        :disabled="savingTerminal"
                        :class="[
                            'w-full bg-white dark:bg-gray-700 rounded-xl p-4 shadow-sm border-2 transition-all flex items-center gap-4',
                            isCurrentTerminal(terminal) 
                                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                                : 'border-gray-200 dark:border-gray-600 hover:border-primary-400',
                            savingTerminal ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer active:scale-95'
                        ]"
                    >
                        <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                        </div>
                        <div class="flex-1 text-left">
                            <h3 class="font-semibold text-gray-900 dark:text-white mb-0.5">
                                {{ terminalDisplayName(terminal) }}
                            </h3>
                            <p v-if="terminal.city_name || terminal.city" class="text-sm text-gray-500 dark:text-gray-400">
                                {{ terminal.city_name || terminal.city }}
                            </p>
                        </div>
                        <div v-if="isCurrentTerminal(terminal)" class="flex items-center gap-2 text-primary-600 dark:text-primary-400">
                            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            <span class="text-sm font-medium">Выбрано</span>
                        </div>
                        <div v-else-if="savingTerminal" class="animate-spin w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full"></div>
                        <svg v-else class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                    </button>
                </div>

                <!-- Empty State -->
                <div v-else class="text-center py-8">
                    <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Точки продажи не найдены
                    </h3>
                    <p class="text-gray-600 dark:text-gray-400 text-sm">
                        В вашей организации нет доступных точек продажи
                    </p>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organization'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'
import usersService from '@/services/users.service'

const router = useRouter()
const authStore = useAuthStore()
const organizationStore = useOrganizationStore()
const notificationStore = useNotificationStore()

const user = computed(() => authStore.user)
const showTerminalModal = ref(false)
const availableTerminals = ref([])
const loadingTerminals = ref(false)
const savingTerminal = ref(false)
const terminalError = ref(null)

const currentTerminal = computed(() => {
    if (!user.value?.terminals || user.value.terminals.length === 0) {
        return null
    }
    return user.value.terminals[0]
})

/** Только человекочитаемое название, без UUID */
function terminalDisplayName(terminal) {
    if (!terminal) return 'Точка продажи'
    const name = (terminal.name || terminal.terminal_group_name || '').trim()
    if (!name) return 'Точка продажи'
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    if (uuidRegex.test(name)) return 'Точка продажи'
    return name
}

const isCurrentTerminal = (terminal) => {
    if (!currentTerminal.value) return false
    const terminalId = terminal.id || terminal.terminal_id
    const currentId = currentTerminal.value.id || currentTerminal.value.terminal_id
    return terminalId === currentId
}

watch(showTerminalModal, async (isOpen) => {
    if (isOpen) {
        await loadTerminals()
    }
})

async function loadTerminals() {
    loadingTerminals.value = true
    terminalError.value = null

    try {
        const data = await organizationStore.fetchTerminals()
        availableTerminals.value = (data || []).filter(t => t.is_active !== false)
    } catch (err) {
        console.error('Load terminals error:', err)
        terminalError.value = organizationStore.error || 'Не удалось загрузить терминалы'
    } finally {
        loadingTerminals.value = false
    }
}

async function selectTerminal(terminal) {
    if (isCurrentTerminal(terminal)) {
        showTerminalModal.value = false
        return
    }

    savingTerminal.value = true
    terminalError.value = null

    try {
        const terminalId = terminal.id || terminal.terminal_id
        
        // Обновляем терминалы пользователя - ставим выбранный терминал первым
        const currentTerminals = user.value?.terminals || []
        const terminalIds = currentTerminals.map(t => typeof t === 'object' ? t.id || t.terminal_id : t)
        
        // Удаляем выбранный терминал из списка, если он там есть
        const filteredIds = terminalIds.filter(id => id !== terminalId)
        
        // Ставим выбранный терминал первым
        const newTerminalIds = [terminalId, ...filteredIds]
        
        // Обновляем пользователя через API
        await usersService.updateProfile({ 
            terminals: newTerminalIds 
        })
        
        // Перезагружаем данные пользователя
        await authStore.fetchCurrentUser(true)
        
        notificationStore.show('Точка продажи успешно изменена')
        showTerminalModal.value = false
    } catch (err) {
        console.error('Select terminal error:', err)
        terminalError.value = err.response?.data?.detail || err.response?.data?.error || 'Не удалось изменить точку продажи'
        telegramService.showAlert(terminalError.value)
    } finally {
        savingTerminal.value = false
    }
}

const goToAddresses = () => {
    router.push('/profile/addresses')
}

const logout = () => {
    telegramService.showConfirm('Вы уверены, что хотите выйти?', () => {
        authStore.logout()
        router.push('/')
        notificationStore.show('Вы вышли из системы')
    })
}
</script>
