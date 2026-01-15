<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
    <div class="text-center">
      <!-- Анимированный логотип -->
      <div class="mb-8">
        <div class="relative w-24 h-24 mx-auto">
          <!-- Внешнее кольцо -->
          <div class="absolute inset-0 border-4 border-primary-200 dark:border-primary-900 rounded-full"></div>
          
          <!-- Вращающееся кольцо -->
          <div class="absolute inset-0 border-4 border-transparent border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
          
          <!-- Иконка -->
          <div class="absolute inset-0 flex items-center justify-center">
            <svg class="w-12 h-12 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Текст -->
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Проверка доступа
      </h2>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Пожалуйста, подождите...
      </p>

      <!-- Прогресс-бар -->
      <div class="max-w-xs mx-auto mb-4">
        <div class="h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div class="h-full bg-primary-600 dark:bg-primary-400 rounded-full animate-pulse" style="width: 70%"></div>
        </div>
      </div>

      <!-- Дополнительная информация -->
      <div class="text-sm text-gray-500 dark:text-gray-400">
        <p>Проверяем вашу регистрацию в системе</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Простой компонент загрузки
</script>