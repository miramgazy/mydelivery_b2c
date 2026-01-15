<template>
  <div class="sticky top-0 z-10 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
    <div class="overflow-x-auto hide-scrollbar">
      <div class="flex gap-2 p-4 min-w-max">
        <!-- Все категории -->
        <button
          @click="selectCategory(null)"
          class="px-4 py-2 rounded-full whitespace-nowrap transition-colors"
          :class="selectedCategory === null 
            ? 'bg-primary-600 text-white' 
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
        >
          Все
        </button>

        <!-- Список категорий -->
        <button
          v-for="category in categories"
          :key="category.subgroup_id"
          @click="selectCategory(category.subgroup_id)"
          class="px-4 py-2 rounded-full whitespace-nowrap transition-colors"
          :class="selectedCategory === category.subgroup_id 
            ? 'bg-primary-600 text-white' 
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
        >
          {{ category.subgroup_name }}
          <span v-if="category.products_count" class="ml-1 text-xs opacity-75">
            ({{ category.products_count }})
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { toRefs } from 'vue'
import telegramService from '@/services/telegram'

const props = defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  selectedCategory: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['select'])

const { categories, selectedCategory } = toRefs(props)

const selectCategory = (categoryId) => {
  telegramService.vibrate('light')
  emit('select', categoryId)
}
</script>

<style scoped>
/* Скрыть скроллбар */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>