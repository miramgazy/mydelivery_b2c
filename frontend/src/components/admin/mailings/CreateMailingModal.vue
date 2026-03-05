<template>
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-black/40">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-3xl w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Создать рассылку
        </h2>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <div class="px-6 py-4 space-y-4 max-h-[70vh] overflow-y-auto">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Название
          </label>
          <input
            v-model="form.title"
            type="text"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Например: Акция на выходные"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            chat_id для тестового сообщения
          </label>
          <input
            v-model="testChatId"
            type="text"
            inputmode="numeric"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Например: 123456789"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Введите ваш chat_id Telegram, чтобы проверить вид сообщения.
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Дата и время отправки
          </label>
          <input
            v-model="form.scheduled_at"
            type="datetime-local"
            :min="minDateTime"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Нельзя выбирать время в прошлом.
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Аудитория
          </label>
          <select
            v-model="audienceType"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="fetchRecipientsCount"
          >
            <option value="all">Всем подписанным</option>
            <option value="newbies">Новички (0 заказов)</option>
            <option value="sleepers_30">Спящие (30+ дней)</option>
            <option value="active_30">Активные (&lt; 30 дней)</option>
          </select>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            <span v-if="isLoadingRecipients">Расчёт аудитории...</span>
            <span v-else-if="recipientsCount !== null">
              Получателей: {{ recipientsCount }}
            </span>
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Текст RU
              </label>
              <button
                type="button"
                class="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                @click="insertPlaceholder('ru')"
              >
                Вставить &#123;&#123;user_name&#125;&#125;
              </button>
            </div>
            <textarea
              v-model="form.message_ru"
              rows="6"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Здравствуйте, {{user_name}}! ..."
            />
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Текст KZ
              </label>
              <button
                type="button"
                class="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                @click="insertPlaceholder('kz')"
              >
                Вставить &#123;&#123;user_name&#125;&#125;
              </button>
            </div>
            <textarea
              v-model="form.message_kz"
              rows="6"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Сәлем, {{user_name}}! ..."
            />
          </div>
        </div>
      </div>

      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <button
          type="button"
          class="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white disabled:opacity-50"
          :disabled="!canSendTest"
          @click="sendTest"
        >
          Отправить тестовое сообщение на chat_id
        </button>

        <div class="space-x-3">
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            @click="$emit('close')"
          >
            Отмена
          </button>
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium rounded-lg text-white shadow-sm"
            :class="isValid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400 cursor-not-allowed'"
            :disabled="!isValid || isSaving"
            @click="save"
          >
            {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import api from '@/services/api'

const emit = defineEmits(['close', 'created'])

const form = reactive({
  title: '',
  scheduled_at: '',
  message_ru: '',
  message_kz: '',
})

const isSaving = ref(false)
const testChatId = ref('')
const audienceType = ref('all')
const recipientsCount = ref(null)
const isLoadingRecipients = ref(false)

const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

const isValid = computed(() => {
  const hasTitle = !!form.title?.trim()
  const hasDate = !!form.scheduled_at
  const inFuture = hasDate && new Date(form.scheduled_at) > new Date()
  const hasText = !!form.message_ru?.trim() || !!form.message_kz?.trim()
  return hasTitle && hasDate && inFuture && hasText
})

const canSendTest = computed(() => {
  const hasText = !!form.message_ru?.trim() || !!form.message_kz?.trim()
  const hasChatId = !!testChatId.value?.trim()
  return hasText && hasChatId
})

const insertPlaceholder = (lang) => {
  const key = `message_${lang}`
  form[key] = (form[key] || '') + ' {{user_name}}'
}

const fetchRecipientsCount = async () => {
  try {
    isLoadingRecipients.value = true
    recipientsCount.value = null
    const { data } = await api.get('/organizations/mailings/count-recipients/', {
      params: { segment: audienceType.value },
    })
    recipientsCount.value = data.count ?? 0
  } catch (e) {
    console.error(e)
    recipientsCount.value = null
  } finally {
    isLoadingRecipients.value = false
  }
}

const save = async () => {
  if (!isValid.value || isSaving.value) return
  isSaving.value = true
  try {
    await api.post('/organizations/mailings/', {
      title: form.title,
      scheduled_at: new Date(form.scheduled_at).toISOString(),
      message_ru: form.message_ru,
      message_kz: form.message_kz,
      audience_type: audienceType.value,
    })
    emit('created')
  } catch (e) {
    console.error(e)
    // здесь можно добавить toast
  } finally {
    isSaving.value = false
  }
}

const sendTest = async () => {
  if (!canSendTest.value) return
  try {
    // Для теста создаём временную рассылку, которая не обязательно попадет в список
    const { data } = await api.post('/organizations/mailings/', {
      title: form.title || 'Тестовая рассылка',
      scheduled_at: new Date(Date.now() + 60_000).toISOString(), // через 1 минуту
      message_ru: form.message_ru,
      message_kz: form.message_kz,
      status: 'draft',
    })
    await api.post(`/organizations/mailings/${data.id}/send-test/`, {
      chat_id: testChatId.value,
    })
    // Здесь можно показать уведомление, что тест ушёл
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  // При первом открытии модалки сразу считаем аудиторию для сегмента по умолчанию
  fetchRecipientsCount()
})
</script>

