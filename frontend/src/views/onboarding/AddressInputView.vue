<template>
  <div class="min-h-screen bg-gray-50 p-4 pb-20">
    <div class="max-w-md mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          {{ t('onboarding.address.title') }}
        </h1>
        <p class="text-gray-600 text-sm">
          {{ t('onboarding.address.hint') }}
        </p>
      </div>

      <!-- Error message -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
        {{ error }}
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4 bg-white rounded-2xl p-6 shadow-sm">
        <!-- Organization (auto from bot context) -->
        <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
          <p class="text-xs text-gray-500 mb-1">{{ t('onboarding.address.venue') }}</p>
          <p class="font-semibold text-gray-900">
            {{ authStore.user?.organization_name || t('onboarding.address.venueAuto') }}
          </p>
        </div>

        <!-- City -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('onboarding.address.city') }} <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.city_id"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :disabled="loadingCities"
          >
            <option value="">{{ t('onboarding.address.citySelect') }}</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
          <p v-if="loadingCities" class="text-xs text-gray-500 mt-1">{{ t('onboarding.address.loadingCities') }}</p>
        </div>

        <!-- Street -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('onboarding.address.street') }} <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.street_name"
            type="text"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :placeholder="t('onboarding.address.streetPlaceholder')"
          />
        </div>

        <!-- House -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('onboarding.address.house') }} <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.house"
            type="text"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :placeholder="t('onboarding.address.housePlaceholder')"
          />
        </div>

        <!-- Flat -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('onboarding.address.flat') }}
          </label>
          <input
            v-model="form.flat"
            type="text"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :placeholder="t('onboarding.address.flatOptional')"
          />
        </div>

        <!-- Comment -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            {{ t('onboarding.address.comment') }}
          </label>
          <textarea
            v-model="form.comment"
            rows="3"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            :placeholder="t('onboarding.address.commentPlaceholder')"
          ></textarea>
        </div>

        <!-- Геопозиция текущего адреса -->
        <div class="pt-2 border-t border-gray-100 dark:border-gray-700">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {{ t('onboarding.address.geolocationHint') }}
          </p>
          <button
            type="button"
            @click="requestLocation"
            :disabled="requestingLocation"
            class="w-full py-3 rounded-xl font-semibold border-2 transition-all flex items-center justify-center gap-2"
            :class="requestingLocation ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white dark:bg-gray-800 text-primary-600 border-primary-200 hover:bg-primary-50 dark:hover:bg-primary-900/20'"
          >
            <span v-if="requestingLocation" class="animate-spin w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full"></span>
            <span v-else-if="locationObtained" class="text-green-600">✓</span>
            <span v-else>📍</span>
            <span>{{ requestingLocation ? t('onboarding.address.geolocationLoading') : t('onboarding.address.geolocationButton') }}</span>
          </button>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 pt-4">
          <button
            type="button"
            @click="handleSkip"
            class="flex-1 px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors"
          >
            {{ t('onboarding.address.skip') }}
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="flex-1 px-4 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ saving ? t('common.saving') : t('onboarding.address.submit') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import deliveryAddressService from '@/services/delivery-address.service'
import { getCities } from '@/services/organization.service'
import telegramService from '@/services/telegram'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  city_id: '',
  street_name: '',
  house: '',
  flat: '',
  comment: ''
})

const saving = ref(false)
const error = ref('')
const cities = ref([])
const loadingCities = ref(false)
const requestingLocation = ref(false)
const locationObtained = ref(false)
const pendingLocation = ref(null) // { latitude, longitude }

onMounted(async () => {
  // Организация теперь определяется по контексту бота.
  // Если вдруг не подцепилась — попробуем перезагрузить профиль.
  if (!authStore.user?.organization) {
    await authStore.fetchCurrentUser()
  }
  
  // Загружаем города организации
  await loadCities()
})

async function loadCities() {
  if (!authStore.user?.organization) {
    return
  }
  
  loadingCities.value = true
  try {
    // Загружаем города с фильтрацией по организации на сервере
    const response = await getCities(authStore.user.organization)
    cities.value = Array.isArray(response) ? response : []
  } catch (err) {
    console.error('Failed to load cities:', err)
    error.value = t('onboarding.address.loadingCitiesError')
  } finally {
    loadingCities.value = false
  }
}

async function handleSubmit() {
  // В текущей архитектуре пользователь должен быть привязан к организации через бота
  if (!authStore.user?.organization) {
    error.value = t('onboarding.address.venueRequired')
    return
  }

  if (!form.city_id || !form.street_name || !form.house) {
    error.value = t('onboarding.address.requiredFields')
    return
  }

  saving.value = true
  error.value = ''

  try {
    // Получаем название города для обратной совместимости
    const city = cities.value.find(c => c.id === form.city_id)
    
    // Создаем адрес доставки (с координатами, если пользователь уточнил геопозицию)
    const addressData = {
      city: form.city_id, // ID города из справочника
      city_name: city ? city.name : '', // Название города для обратной совместимости
      street_name: form.street_name,
      house: form.house,
      flat: form.flat,
      comment: form.comment,
      is_default: true
    }
    if (pendingLocation.value?.latitude != null && pendingLocation.value?.longitude != null) {
      addressData.latitude = pendingLocation.value.latitude
      addressData.longitude = pendingLocation.value.longitude
    }
    await deliveryAddressService.createAddress(addressData)
    
    // Обновляем данные пользователя
    await authStore.fetchCurrentUser()
    
    // Переходим к выбору терминала
    router.push('/onboarding/terminal')
  } catch (err) {
    console.error('Save address error:', err)
    error.value = err.response?.data?.detail || t('onboarding.address.saveError')
  } finally {
    saving.value = false
  }
}

async function requestLocation() {
  if (requestingLocation.value) return
  requestingLocation.value = true
  locationObtained.value = false
  pendingLocation.value = null
  try {
    const location = await telegramService.requestLocation()
    if (location?.latitude != null && location?.longitude != null) {
      pendingLocation.value = { latitude: location.latitude, longitude: location.longitude }
      locationObtained.value = true
      telegramService.showAlert(t('onboarding.address.geolocationSuccess'))
    } else {
      telegramService.showAlert(t('onboarding.address.geolocationFailed'))
    }
  } catch (err) {
    console.error('Geolocation error', err)
    telegramService.showAlert(err.message || t('onboarding.address.geolocationFailed'))
  } finally {
    requestingLocation.value = false
  }
}

function handleSkip() {
  // Пропускаем ввод адреса, переходим к выбору терминала
  router.push('/onboarding/terminal')
}
</script>
