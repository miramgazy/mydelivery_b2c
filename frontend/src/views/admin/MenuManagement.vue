<template>
  <div class="max-w-6xl space-y-6">
    <!-- Table: all menus -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Меню организации</h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Список меню. Активное меню отображается в TMA и терминалах. При активации одного остальные деактивируются.
        </p>
      </div>
      <div class="p-6 overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="text-gray-600 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="py-3 px-2 font-medium">Название</th>
              <th class="py-3 px-2 font-medium">Тип</th>
              <th class="py-3 px-2 font-medium">Ценовая категория</th>
              <th class="py-3 px-2 font-medium">Статус</th>
              <th class="py-3 px-2 font-medium w-24">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="menusLoading" class="border-b border-gray-200 dark:border-gray-700">
              <td colspan="5" class="py-8 text-center text-gray-500">
                <Icon icon="mdi:loading" class="w-6 h-6 animate-spin inline" /> Загрузка…
              </td>
            </tr>
            <tr
              v-else-if="!menusList.length"
              class="border-b border-gray-200 dark:border-gray-700"
            >
              <td colspan="5" class="py-8 text-center text-gray-500">Нет меню</td>
            </tr>
            <tr
              v-for="menu in menusList"
              :key="menu.menu_id"
              class="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50"
            >
              <td class="py-3 px-2 font-medium text-gray-900 dark:text-white">{{ menu.menu_name }}</td>
              <td class="py-3 px-2">
                <span class="text-gray-700 dark:text-gray-300">
                  {{ menu.source_type_display || (menu.source_type === 'external' ? 'Внешнее' : 'Номенклатура') }}
                </span>
              </td>
              <td class="py-3 px-2 text-gray-600 dark:text-gray-400">
                {{ menu.price_category_name || '—' }}
              </td>
              <td class="py-3 px-2">
                <button
                  type="button"
                  role="switch"
                  :aria-checked="menu.is_active"
                  :disabled="menuToggleId === menu.menu_id"
                  @click="toggleMenuActive(menu)"
                  class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                  :class="menu.is_active ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'"
                >
                  <span
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition"
                    :class="menu.is_active ? 'translate-x-5' : 'translate-x-1'"
                  />
                </button>
              </td>
              <td class="py-3 px-2">
                <button
                  type="button"
                  :disabled="deleteMenuId === menu.menu_id"
                  @click="confirmDeleteMenu(menu)"
                  class="p-2 rounded-lg text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 disabled:opacity-50"
                  title="Удалить меню"
                >
                  <Icon icon="mdi:delete-outline" class="w-5 h-5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Success / Error -->
    <div
      v-if="successMessage"
      class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2 text-green-800 dark:text-green-200"
    >
      <Icon icon="mdi:check-circle" class="w-5 h-5 flex-shrink-0" />
      <span>{{ successMessage }}</span>
    </div>
    <div
      v-if="error"
      class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-2 text-red-800 dark:text-red-200"
    >
      <Icon icon="mdi:alert-circle" class="w-5 h-5 flex-shrink-0" />
      <span>{{ error }}</span>
    </div>

    <!-- Load from external menu -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Загрузить из внешнего меню (iiko)</h3>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Выберите внешнее меню. Если доступна ценовая категория — можно выбрать её; иначе будут использованы доступные цены из меню.
        </p>
      </div>
      <div class="p-6">
        <button
          type="button"
          :disabled="loading"
          @click="openExternalModal"
          class="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
        >
          <Icon :icon="loading ? 'mdi:loading' : 'mdi:menu'" :class="{ 'animate-spin': loading }" class="w-5 h-5" />
          Загрузить из внешнего меню
        </button>
      </div>
    </div>

    <!-- Modal: external menu + price category -->
    <div
      v-if="showExternalModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="showExternalModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Внешнее меню</h3>
          <button type="button" @click="showExternalModal = false" class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600">
            <Icon icon="mdi:close" class="w-5 h-5" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Меню</label>
            <select
              v-model="externalForm.external_menu_id"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2"
              @change="externalForm.price_category_id = ''"
            >
              <option value="">— Выберите меню —</option>
              <option v-for="m in externalMenus" :key="m.external_menu_id" :value="m.external_menu_id">
                {{ m.name }}
              </option>
            </select>
          </div>
          <div v-if="currentExternalMenuPriceCategories.length > 0">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Ценовая категория (необязательно)</label>
            <select
              v-model="externalForm.price_category_id"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2"
            >
              <option value="">— Без выбора (любые доступные цены) —</option>
              <option
                v-for="pc in currentExternalMenuPriceCategories"
                :key="pc.id"
                :value="pc.id"
              >
                {{ pc.name || pc.id }}
              </option>
            </select>
          </div>
          <div v-else-if="externalForm.external_menu_id" class="text-sm text-gray-500 dark:text-gray-400">
            Ценовые категории для этого меню не загружены — будут использованы доступные цены.
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              :disabled="!externalForm.external_menu_id || loading"
              @click="submitExternalMenu"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon v-if="loading" icon="mdi:loading" class="w-5 h-5 animate-spin" />
              Загрузить
            </button>
            <button type="button" @click="showExternalModal = false" class="px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg">
              Отмена
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Nomenclature: by groups -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Меню из номенклатуры (по группам)</h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Получите структуру и выберите группы для загрузки
        </p>
      </div>
      <div class="p-6">
        <div class="mb-6">
          <button
            type="button"
            @click="handleFetchMenuStructure"
            :disabled="loading"
            class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            <Icon :icon="loading && step === 1 ? 'mdi:loading' : 'mdi:refresh'" :class="{ 'animate-spin': loading && step === 1 }" class="w-5 h-5" />
            Загрузить структуру
          </button>
        </div>

        <div v-if="menuGroups && menuGroups.length > 0">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Выберите группы</h3>
            <button type="button" @click="toggleSelectAll" class="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline">
              {{ isAllSelected ? 'Снять выделение' : 'Выбрать все' }}
            </button>
          </div>
          <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="group in menuGroups"
              :key="group.id"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-3 hover:border-blue-500 dark:hover:border-blue-400 transition-colors cursor-pointer"
              :class="{ 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20': isSelected(group.id) }"
              @click="toggleGroup(group.id)"
            >
              <div class="flex items-start gap-3">
                <Icon :icon="isSelected(group.id) ? 'mdi:checkbox-marked' : 'mdi:checkbox-blank-outline'" class="w-5 h-5 mt-0.5" :class="isSelected(group.id) ? 'text-blue-600' : 'text-gray-400'" />
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ group.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Подкатегорий: {{ group.childrenCount || 0 }}</p>
                </div>
              </div>
            </div>
          </div>
          <button
            type="button"
            @click="handleLoadSelected"
            :disabled="selectedGroups.length === 0 || loading"
            class="mt-6 flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon :icon="loading && step === 2 ? 'mdi:loading' : 'mdi:download'" :class="{ 'animate-spin': loading && step === 2 }" class="w-5 h-5" />
            Загрузить выбранные ({{ selectedGroups.length }})
          </button>
        </div>

        <div v-else-if="!loading && step === 0" class="py-12 text-center text-gray-500 dark:text-gray-400">
          <Icon icon="mdi:food-off" class="w-16 h-16 mx-auto mb-4" />
          <p class="text-lg font-medium">Структура меню не загружена</p>
          <p class="text-sm">Нажмите «Загрузить структуру»</p>
        </div>
        <div v-if="loading && step === 1" class="flex justify-center py-12">
          <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const menusList = ref([])
const menusLoading = ref(false)
const menuToggleId = ref(null)
const deleteMenuId = ref(null)
const showExternalModal = ref(false)
const externalMenus = computed(() => organizationStore.externalMenus || [])
const currentExternalMenuPriceCategories = computed(() => {
  const menu = externalMenus.value.find(m => m.external_menu_id === externalForm.value.external_menu_id)
  return menu?.price_categories || []
})
const externalForm = ref({
  external_menu_id: '',
  price_category_id: '',
})

const selectedGroups = ref([])
const successMessage = ref('')
const error = ref(null)
const step = ref(0)
const loading = computed(() => organizationStore.loading)
const menuGroups = computed(() => organizationStore.menuGroups || [])

const isSelected = (id) => selectedGroups.value.includes(id)
const isAllSelected = computed(() => menuGroups.value.length > 0 && selectedGroups.value.length === menuGroups.value.length)

function setError(e) {
  error.value = e || organizationStore.error
}
function setSuccess(msg) {
  successMessage.value = msg
  setTimeout(() => { successMessage.value = '' }, 4000)
}

async function loadMenusList() {
  menusLoading.value = true
  try {
    const data = await organizationStore.fetchMenus(true)
    menusList.value = Array.isArray(data) ? data : []
  } catch {
    menusList.value = []
  } finally {
    menusLoading.value = false
  }
}

async function toggleMenuActive(menu) {
  const id = menu.menu_id != null ? String(menu.menu_id) : null
  if (!id) return
  menuToggleId.value = id
  error.value = null
  try {
    await organizationStore.updateMenu(id, { is_active: !menu.is_active })
    menu.is_active = !menu.is_active
    setSuccess('Статус меню обновлён')
    await loadMenusList()
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.response?.data?.error || e?.message || 'Не удалось обновить меню'
    setError(typeof msg === 'object' ? JSON.stringify(msg) : msg)
  } finally {
    menuToggleId.value = null
  }
}

function confirmDeleteMenu(menu) {
  const name = menu.menu_name || 'меню'
  if (!confirm(`Удалить меню «${name}»? Будут удалены все категории, блюда и модификаторы этого меню. Это действие нельзя отменить.`)) return
  const id = menu.menu_id != null ? String(menu.menu_id) : null
  if (!id) return
  deleteMenuId.value = id
  error.value = null
  organizationStore.deleteMenu(id).then(() => {
    setSuccess('Меню удалено')
    return loadMenusList()
  }).catch(() => {
    setError(organizationStore.error || 'Не удалось удалить меню')
  }).finally(() => {
    deleteMenuId.value = null
  })
}

async function openExternalModal() {
  error.value = null
  showExternalModal.value = true
  externalForm.value = { external_menu_id: '', price_category_id: '' }
  try {
    await organizationStore.fetchExternalMenus()
  } catch (e) {
    setError('Не удалось загрузить список внешних меню')
  }
}

async function submitExternalMenu() {
  const { external_menu_id, price_category_id } = externalForm.value
  if (!external_menu_id) return
  error.value = null
  const menu = externalMenus.value.find(m => m.external_menu_id === external_menu_id)
  const priceCategoryName = price_category_id
    ? (menu?.price_categories?.find(pc => pc.id === price_category_id)?.name || '')
    : ''
  const payload = {
    external_menu_id,
    menu_name: menu?.name,
  }
  if (price_category_id) {
    payload.price_category_id = price_category_id
    payload.price_category_name = priceCategoryName
  }
  try {
    await organizationStore.loadMenuFromIiko(payload)
    setSuccess('Внешнее меню успешно загружено')
    showExternalModal.value = false
    await loadMenusList()
  } catch (e) {
    setError()
  }
}

function toggleGroup(id) {
  if (isSelected(id)) {
    selectedGroups.value = selectedGroups.value.filter(g => g !== id)
  } else {
    selectedGroups.value.push(id)
  }
}
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedGroups.value = []
  } else {
    selectedGroups.value = menuGroups.value.map(g => g.id)
  }
}

async function handleFetchMenuStructure() {
  error.value = null
  successMessage.value = ''
  step.value = 1
  selectedGroups.value = []
  try {
    await organizationStore.fetchMenuGroups()
    setSuccess('Структура меню получена')
  } catch {
    setError('Не удалось получить структуру меню')
  } finally {
    step.value = 0
  }
}

async function handleLoadSelected() {
  if (selectedGroups.value.length === 0) return
  error.value = null
  successMessage.value = ''
  step.value = 2
  try {
    const result = await organizationStore.loadMenuGroups(selectedGroups.value)
    setSuccess(result?.message || 'Меню синхронизировано')
    await loadMenusList()
  } catch {
    setError('Не удалось загрузить меню')
  } finally {
    step.value = 0
  }
}

onMounted(() => {
  loadMenusList()
})
</script>
