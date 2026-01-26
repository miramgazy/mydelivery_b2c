<template>
  <div class="max-w-4xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
        Настройки организации
      </h2>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
          <Icon icon="mdi:alert-circle" class="w-5 h-5" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Success -->
      <div
        v-if="successMessage"
        class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-green-800 dark:text-green-200">
          <Icon icon="mdi:check-circle" class="w-5 h-5" />
          <span>{{ successMessage }}</span>
        </div>
      </div>

      <!-- Form -->
      <form v-if="!loading" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Organization ID -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            ID организации в IIKO
          </label>
          <input
            v-model="form.iiko_organization_id"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите ID организации"
            required
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            UUID вашей организации в системе iiko
          </p>
        </div>

        <!-- API Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API ключ от iiko cloud API
          </label>
          <div class="relative">
            <input
              v-model="form.api_key"
              :type="showApiKey ? 'text' : 'password'"
              class="w-full px-4 py-2.5 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Введите API ключ"
              required
            />
            <button
              type="button"
              @click="showApiKey = !showApiKey"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Icon :icon="showApiKey ? 'mdi:eye-off' : 'mdi:eye'" class="w-5 h-5" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            API ключ для доступа к iiko Cloud
          </p>
        </div>

        <!-- Organization Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Название организации
          </label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите название"
          />
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Телефон
          </label>
          <input
            v-model="form.phone"
            type="tel"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="+7 (XXX) XXX-XX-XX"
          />
        </div>

        <!-- Address -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Адрес
          </label>
          <input
            v-model="form.address"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите адрес"
          />
        </div>

        <!-- Bot Token -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Токен Telegram бота
          </label>
          <div class="relative">
            <input
              v-model="form.bot_token"
              :type="showBotToken ? 'text' : 'password'"
              autocomplete="off"
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              class="w-full px-4 py-2.5 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Введите токен бота"
            />
            <button
              type="button"
              @click="showBotToken = !showBotToken"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Icon :icon="showBotToken ? 'mdi:eye-off' : 'mdi:eye'" class="w-5 h-5" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Уникальный токен Telegram бота для этой организации
          </p>
        </div>

        <!-- Bot Username -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Юзернейм Telegram бота
          </label>
          <input
            v-model="form.bot_username"
            type="text"
            autocomplete="off"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="username"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Юзернейм бота (без @) для формирования ссылок
          </p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4 pt-4">
          <button
            type="submit"
            :disabled="saving"
            class="flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700
                   text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon
              :icon="saving ? 'mdi:loading' : 'mdi:content-save'"
              :class="{ 'animate-spin': saving }"
              class="w-5 h-5"
            />
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'

const organizationStore = useOrganizationStore()

const form = ref({
  iiko_organization_id: '',
  api_key: '',
  name: '',
  phone: '',
  address: '',
  bot_token: '',
  bot_username: ''
})

const showApiKey = ref(false)
const showBotToken = ref(false)
const saving = ref(false)
const successMessage = ref('')
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadOrganization()
})

const loadOrganization = async () => {
  loading.value = true
  error.value = null

  try {
    const org = await organizationStore.fetchOrganization()
    if (org) {
      form.value = {
        iiko_organization_id: org.iiko_organization_id || '',
        api_key: org.api_key || '',
        name: org.name || '',
        phone: org.phone || '',
        address: org.address || '',
        bot_token: org.bot_token || '',
        bot_username: org.bot_username || ''
      }
    }
  } catch (err) {
    error.value = organizationStore.error
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  saving.value = true
  error.value = null
  successMessage.value = ''

  try {
    const payload = {
      ...form.value,
      bot_token: (form.value.bot_token || '').trim(),
      bot_username: (form.value.bot_username || '').trim().replace(/^@+/, '')
    }

    await organizationStore.updateOrganization(payload)
    // После сохранения перечитываем данные с сервера (чтобы точно увидеть, что сохранилось)
    await loadOrganization()
    successMessage.value = 'Настройки успешно сохранены'

    // Hide success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось сохранить настройки'
  } finally {
    saving.value = false
  }
}
</script>
