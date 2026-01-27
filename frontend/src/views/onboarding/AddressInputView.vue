<template>
  <div class="min-h-screen bg-gray-50 p-4 pb-20">
    <div class="max-w-md mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          Адрес доставки
        </h1>
        <p class="text-gray-600 text-sm">
          Укажите адрес для доставки заказов
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
          <p class="text-xs text-gray-500 mb-1">Заведение</p>
          <p class="font-semibold text-gray-900">
            {{ authStore.user?.organization_name || 'Определяется автоматически' }}
          </p>
        </div>

        <!-- City -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Город <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.city_id"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
            :disabled="loadingCities"
          >
            <option value="">Выберите город</option>
            <option v-for="city in cities" :key="city.id" :value="city.id">
              {{ city.name }}
            </option>
          </select>
          <p v-if="loadingCities" class="text-xs text-gray-500 mt-1">Загрузка городов...</p>
        </div>

        <!-- Street -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Улица <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.street_name"
            type="text"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Название улицы"
          />
        </div>

        <!-- House -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Дом <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.house"
            type="text"
            required
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Например: 15А"
          />
        </div>

        <!-- Flat -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Квартира/Офис
          </label>
          <input
            v-model="form.flat"
            type="text"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Необязательно"
          />
        </div>

        <!-- Comment -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Комментарий
          </label>
          <textarea
            v-model="form.comment"
            rows="3"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Дополнительная информация для курьера"
          ></textarea>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3 pt-4">
          <button
            type="button"
            @click="handleSkip"
            class="flex-1 px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors"
          >
            Пропустить
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
            <span>{{ saving ? 'Сохранение...' : 'Сохранить' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import deliveryAddressService from '@/services/delivery-address.service'
import { getCities } from '@/services/organization.service'

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
    error.value = 'Не удалось загрузить список городов'
  } finally {
    loadingCities.value = false
  }
}

async function handleSubmit() {
  // В текущей архитектуре пользователь должен быть привязан к организации через бота
  if (!authStore.user?.organization) {
    error.value = 'Не удалось определить заведение. Откройте Mini App через нужного бота.'
    return
  }

  if (!form.city_id || !form.street_name || !form.house) {
    error.value = 'Заполните обязательные поля: город, улица, дом'
    return
  }

  saving.value = true
  error.value = ''

  try {
    // Получаем название города для обратной совместимости
    const city = cities.value.find(c => c.id === form.city_id)
    
    // Создаем адрес доставки
    await deliveryAddressService.createAddress({
      city: form.city_id, // ID города из справочника
      city_name: city ? city.name : '', // Название города для обратной совместимости
      street_name: form.street_name,
      house: form.house,
      flat: form.flat,
      comment: form.comment,
      is_default: true
    })
    
    // Обновляем данные пользователя
    await authStore.fetchCurrentUser()
    
    // Переходим к выбору терминала
    router.push('/onboarding/terminal')
  } catch (err) {
    console.error('Save address error:', err)
    error.value = err.response?.data?.detail || 'Не удалось сохранить данные. Попробуйте еще раз.'
  } finally {
    saving.value = false
  }
}

function handleSkip() {
  // Пропускаем ввод адреса, переходим к выбору терминала
  router.push('/onboarding/terminal')
}
</script>
