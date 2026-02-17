<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-4 sticky top-0 z-20">
      <button @click="goBack" class="p-2 -ml-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">Мои адреса</h1>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          Можно сохранить до 3 адресов. Нажмите на адрес, чтобы сделать его основным.
        </p>
      </div>
    </div>

    <div class="p-4 space-y-4">
      <!-- Error -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
        {{ error }}
      </div>

      <!-- List -->
      <div class="space-y-2">
        <div
          v-for="addr in addresses"
          :key="addr.id"
          class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 flex items-start gap-3"
        >
          <button
            class="flex-1 text-left"
            @click="makeDefault(addr)"
            :disabled="addr.is_default || settingDefault"
          >
            <div class="flex items-center gap-2">
              <div
                class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
                :class="addr.is_default ? 'border-primary-600' : 'border-gray-300 dark:border-gray-600'"
              >
                <div v-if="addr.is_default" class="w-2.5 h-2.5 bg-primary-600 rounded-full"></div>
              </div>
              <div class="font-semibold text-gray-900 dark:text-white text-sm">
                {{ addr.full_address || formatAddress(addr) }}
              </div>
              <!-- Индикация верификации -->
              <span v-if="addr.is_verified" class="text-lg" title="Адрес верифицирован">✅</span>
              <span v-else class="text-lg" title="Адрес не верифицирован">⚠️</span>
              <span v-if="addr.is_default" class="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full border border-primary-100">
                Основной
              </span>
            </div>
            <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              <span v-if="addr.entrance">Подъезд {{ addr.entrance }}</span>
              <span v-if="addr.entrance && addr.floor"> · </span>
              <span v-if="addr.floor">Этаж {{ addr.floor }}</span>
              <span v-if="(addr.entrance || addr.floor) && addr.comment"> · </span>
              <span v-if="addr.comment">{{ addr.comment }}</span>
            </div>
          </button>

          <!-- Delete -->
          <button
            class="p-2 rounded-full"
            :class="canDelete ? 'hover:bg-red-50 text-red-600' : 'text-gray-300 cursor-not-allowed'"
            :disabled="!canDelete || deletingId === addr.id"
            @click="deleteAddress(addr)"
            title="Удалить"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="!loading && addresses.length === 0" class="p-4 bg-white dark:bg-gray-800 rounded-xl text-sm text-gray-500 dark:text-gray-400">
          Адресов пока нет. Добавьте первый адрес.
        </div>
      </div>

      <!-- Кнопка "Уточнить геопозицию" -->
      <button
        v-if="addresses.length > 0"
        @click="requestLocation"
        :disabled="requestingLocation"
        class="w-full py-3 rounded-xl font-semibold border-2 transition-all flex items-center justify-center gap-2"
        :class="requestingLocation ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white dark:bg-gray-800 text-primary-600 border-primary-200 hover:bg-primary-50'"
      >
        <span v-if="requestingLocation" class="animate-spin w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full"></span>
        <span v-else>📍 Уточнить геопозицию</span>
      </button>

      <!-- Add button -->
      <button
        class="w-full py-3 rounded-xl font-semibold border-2 transition-all"
        :class="maxReached ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white dark:bg-gray-800 text-primary-600 border-primary-200 hover:bg-primary-50'"
        :disabled="maxReached"
        @click="showForm = !showForm"
      >
        Добавить другой адрес
      </button>

      <!-- Create form -->
      <div v-if="showForm" class="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="font-bold text-gray-900 dark:text-white">Новый адрес</h2>
          <button @click="showForm = false" class="text-gray-400 hover:text-gray-600">Закрыть</button>
        </div>

        <div class="grid grid-cols-1 gap-3">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Город *</label>
            <input v-model="form.city_name" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Улица *</label>
            <input v-model="form.street_name" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Дом *</label>
              <input v-model="form.house" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Квартира</label>
              <input v-model="form.flat" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Подъезд</label>
              <input v-model="form.entrance" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Этаж</label>
              <input v-model="form.floor" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Комментарий</label>
            <textarea v-model="form.comment" rows="2" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"></textarea>
          </div>
        </div>

        <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input type="checkbox" v-model="form.is_default" class="rounded" />
          Сделать основным
        </label>

        <button
          class="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-bold rounded-xl flex items-center justify-center gap-2"
          :disabled="saving"
          @click="createAddress"
        >
          <span v-if="saving" class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
          <span v-else>Сохранить</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import deliveryAddressService from '@/services/delivery-address.service'
import telegramService from '@/services/telegram'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const addresses = ref([])
const loading = ref(false)
const error = ref('')

const showForm = ref(false)
const saving = ref(false)
const settingDefault = ref(false)
const deletingId = ref(null)
const requestingLocation = ref(false)

const form = reactive({
  city_name: '',
  street_name: '',
  house: '',
  flat: '',
  entrance: '',
  floor: '',
  comment: '',
  is_default: false
})

const maxReached = computed(() => addresses.value.length >= 3)
const canDelete = computed(() => addresses.value.length > 1)

function formatAddress(a) {
  const parts = []
  if (a.city_name) parts.push(a.city_name)
  if (a.street_name) parts.push(a.street_name)
  if (a.house) parts.push(a.house)
  if (a.flat) parts.push(`кв. ${a.flat}`)
  return parts.filter(Boolean).join(', ')
}

function goBack() {
  const returnTo = route.query?.return
  if (returnTo) {
    router.push(String(returnTo))
    return
  }
  router.back()
}

async function loadAddresses() {
  loading.value = true
  error.value = ''
  try {
    const data = await deliveryAddressService.getAddresses()
    addresses.value = Array.isArray(data) ? data : (data?.results ?? [])
  } catch (err) {
    console.error('Failed to load addresses', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить адреса'
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await loadAddresses()
  // Синхронизируем user.addresses, чтобы Checkout/Profile сразу увидели обновления
  await authStore.fetchCurrentUser()
}

async function makeDefault(addr) {
  if (addr.is_default || settingDefault.value) return
  settingDefault.value = true
  try {
    await deliveryAddressService.setDefault(addr.id)
    await refreshAll()
  } catch (err) {
    console.error('Set default failed', err)
    telegramService.showAlert(err.response?.data?.detail || 'Не удалось установить адрес основным')
  } finally {
    settingDefault.value = false
  }
}

function deleteAddress(addr) {
  if (!canDelete.value || deletingId.value) return
  telegramService.showConfirm('Удалить этот адрес?', async () => {
    deletingId.value = addr.id
    try {
      await deliveryAddressService.deleteAddress(addr.id)
      await refreshAll()
    } catch (err) {
      console.error('Delete address failed', err)
      telegramService.showAlert(err.response?.data?.detail || 'Не удалось удалить адрес')
    } finally {
      deletingId.value = null
    }
  })
}

async function createAddress() {
  if (saving.value) return
  if (maxReached.value) {
    telegramService.showAlert('Можно сохранить не более 3 адресов')
    return
  }
  if (!form.city_name || !form.street_name || !form.house) {
    telegramService.showAlert('Заполните обязательные поля: город, улица, дом')
    return
  }

  saving.value = true
  try {
    await deliveryAddressService.createAddress({
      city_name: form.city_name,
      street_name: form.street_name,
      house: form.house,
      flat: form.flat,
      entrance: form.entrance,
      floor: form.floor,
      comment: form.comment,
      is_default: !!form.is_default
    })

    // reset
    form.city_name = ''
    form.street_name = ''
    form.house = ''
    form.flat = ''
    form.entrance = ''
    form.floor = ''
    form.comment = ''
    form.is_default = false
    showForm.value = false

    await refreshAll()
  } catch (err) {
    console.error('Create address failed', err)
    telegramService.showAlert(err.response?.data?.detail || 'Не удалось сохранить адрес')
  } finally {
    saving.value = false
  }
}

async function requestLocation() {
  if (requestingLocation.value) return
  
  // Проверяем, есть ли адреса для обновления
  if (addresses.value.length === 0) {
    telegramService.showAlert('Сначала добавьте адрес доставки')
    return
  }
  
  requestingLocation.value = true
  try {
    // Запрашиваем геолокацию через браузерный API (миниап может получить координаты напрямую)
    const location = await telegramService.requestLocation()
    
    if (!location || !location.latitude || !location.longitude) {
      telegramService.showAlert('Не удалось получить координаты')
      return
    }
    
    // Находим адрес по умолчанию или первый адрес
    const addressToUpdate = addresses.value.find(addr => addr.is_default) || addresses.value[0]
    
    if (!addressToUpdate) {
      telegramService.showAlert('Не найден адрес для обновления')
      return
    }
    
    // Обновляем координаты через отдельный endpoint (избегаем проблем с PATCH и валидацией)
    await deliveryAddressService.updateCoordinates(
      addressToUpdate.id,
      location.latitude,
      location.longitude
    )
    
    // Обновляем список адресов
    await refreshAll()
    
    telegramService.showAlert('Геопозиция успешно сохранена! Адрес верифицирован.')
  } catch (err) {
    console.error('Request location failed', err)
    const data = err.response?.data
    let errorMessage = 'Ошибка при сохранении геолокации'
    if (data?.detail) {
      errorMessage = typeof data.detail === 'string' ? data.detail : (Array.isArray(data.detail) ? data.detail.join(', ') : JSON.stringify(data.detail))
    } else if (data && typeof data === 'object') {
      const parts = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      if (parts.length) errorMessage = parts.join('; ')
    } else if (err.message) {
      errorMessage = err.message
    }
    telegramService.showAlert(errorMessage)
  } finally {
    requestingLocation.value = false
  }
}

onMounted(async () => {
  await loadAddresses()
})
</script>

