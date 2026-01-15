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
    <div v-else-if="filteredUsers.length === 0" class="text-center py-12 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-dashed border-gray-200 dark:border-gray-700">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1">Пользователи не найдены</h3>
        <p class="text-sm text-gray-500">Попробуйте изменить параметры поиска</p>
    </div>

    <!-- Users List -->
    <div v-else class="space-y-4">
        <div 
          v-for="user in filteredUsers" 
          :key="user.id" 
          class="bg-white dark:bg-gray-800 p-4 rounded-2xl shadow-sm flex items-center justify-between border border-gray-100 dark:border-gray-700 transition-transform active:scale-[0.98]"
        >
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-bold text-lg">
                    {{ (user.first_name || user.username || 'U')[0].toUpperCase() }}
                </div>
                <div>
                    <h3 class="font-bold text-gray-900 dark:text-white leading-tight">
                        {{ user.full_name || user.username }}
                    </h3>
                    <div class="flex items-center gap-2 mt-1">
                        <span class="text-[10px] px-1.5 py-0.5 rounded-md font-bold uppercase transition-colors"
                          :class="{
                            'bg-blue-100 text-blue-700': user.role_name === 'org_admin',
                            'bg-green-100 text-green-700': user.role_name === 'customer',
                            'bg-purple-100 text-purple-700': user.role_name === 'superadmin'
                          }"
                        >
                            {{ user.role_display }}
                        </span>
                        <p v-if="user.phone" class="text-xs text-gray-500">{{ user.phone }}</p>
                    </div>
                </div>
            </div>
            <button 
              @click="editUser(user)"
              class="w-10 h-10 flex items-center justify-center text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
            </button>
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
import { ref, computed, onMounted, reactive } from 'vue'
import usersService from '@/services/users.service'
import { useOrganizationStore } from '@/stores/organization'

const loading = ref(true)
const users = ref([])
const allRoles = ref([])
const organizationStore = useOrganizationStore()
const availableTerminals = computed(() => organizationStore.terminals)
const activeFilter = ref('all')
const searchQuery = ref('')

const showCreateModal = ref(false)
const editingUser = ref(null)
const modalLoading = ref(false)
const modalError = ref('')

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

const filteredUsers = computed(() => {
    let result = Array.isArray(users.value) ? users.value : (users.value?.results || [])

    if (activeFilter.value !== 'all') {
        result = result.filter(u => u.role_name === activeFilter.value)
    }

    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(u => 
            (u.full_name?.toLowerCase().includes(query)) ||
            (u.username?.toLowerCase().includes(query)) ||
            (u.phone?.includes(query))
        )
    }

    return result
})

async function fetchData() {
    loading.value = true
    try {
        const [usersData, rolesData] = await Promise.all([
            usersService.getUsers(),
            usersService.getRoles(),
            organizationStore.fetchTerminals()
        ])
        
        // Handle paginated or non-paginated response
        users.value = Array.isArray(usersData) ? usersData : (usersData.results || [])
        allRoles.value = Array.isArray(rolesData) ? rolesData : (rolesData.results || [])
        
        // По умолчанию ставим роль "клиент" для формы
        const customerRole = allRoles.value.find(r => r.role_name === 'customer')
        if (customerRole) form.role = customerRole.id
    } catch (err) {
        console.error('Fetch error:', err)
    } finally {
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
        
        await fetchData()
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

