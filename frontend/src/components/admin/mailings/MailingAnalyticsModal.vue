<template>
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-black/40">
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-lg w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Аналитика рассылки
        </h2>
        <button
          type="button"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <div class="px-6 py-4 space-y-3">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Название</p>
          <p class="text-sm font-medium text-gray-900 dark:text-white">
            {{ mailing.title }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-2">
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Всего получателей
            </p>
            <p class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ mailing.total_recipients || 0 }}
            </p>
          </div>
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Отправлено всего
            </p>
            <p class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ (mailing.sent_ru || 0) + (mailing.sent_kz || 0) }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-4">
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              RU
            </p>
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ mailing.sent_ru || 0 }}
            </p>
          </div>
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              KZ
            </p>
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ mailing.sent_kz || 0 }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-4">
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Технические ошибки
            </p>
            <p class="text-lg font-semibold text-red-600 dark:text-red-400">
              {{ mailing.failed_count || 0 }}
            </p>
          </div>
          <div class="space-y-1">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Отписались (403)
            </p>
            <p class="text-lg font-semibold text-orange-600 dark:text-orange-400">
              {{ mailing.unsubscribed_count || 0 }}
            </p>
          </div>
        </div>
      </div>

      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-white"
          @click="$emit('close')"
        >
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  mailing: {
    type: Object,
    required: true,
  },
})
</script>

