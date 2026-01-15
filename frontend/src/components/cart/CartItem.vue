<template>
  <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
    <div class="flex gap-3">
      <!-- Изображение -->
      <div class="w-20 h-20 rounded-lg bg-gray-200 dark:bg-gray-600 flex-shrink-0 overflow-hidden">
        <img 
          v-if="item.image_url" 
          :src="item.image_url" 
          :alt="item.product_name"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      </div>

      <!-- Информация -->
      <div class="flex-1 min-w-0">
        <!-- Название -->
        <h4 class="font-semibold text-gray-900 dark:text-white mb-1">
          {{ item.product_name }}
        </h4>

        <!-- Модификаторы -->
        <div v-if="item.modifiers && item.modifiers.length > 0" class="mb-2">
          <div 
            v-for="modifier in item.modifiers" 
            :key="modifier.modifier_id"
            class="text-xs text-gray-600 dark:text-gray-400"
          >
            + {{ modifier.modifier_name }}
            <span v-if="modifier.quantity > 1">x{{ modifier.quantity }}</span>
            <span v-if="modifier.price > 0">(+{{ formatPrice(modifier.price) }} ₸)</span>
          </div>
        </div>

        <!-- Цена и количество -->
        <div class="flex items-center justify-between">
          <!-- Количество -->
          <div class="flex items-center gap-2 bg-white dark:bg-gray-600 rounded-lg p-1">
            <button
              @click="$emit('decrement', index)"
              class="w-8 h-8 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-500 rounded-lg transition-colors"
            >
              <svg v-if="item.quantity > 1" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
              <svg v-else class="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>

            <span class="font-semibold text-gray-900 dark:text-white min-w-[2rem] text-center">
              {{ item.quantity }}
            </span>

            <button
              @click="$emit('increment', index)"
              class="w-8 h-8 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-500 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          <!-- Цена -->
          <div class="text-right">
            <div class="font-bold text-gray-900 dark:text-white">
              {{ formatPrice(itemTotal) }} ₸
            </div>
            <div v-if="item.quantity > 1" class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatPrice(item.price) }} ₸ × {{ item.quantity }}
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопка удаления -->
      <button
        @click="$emit('remove', index)"
        class="self-start p-2 hover:bg-red-50 dark:hover:bg-red-900 text-red-600 dark:text-red-400 rounded-lg transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})

defineEmits(['increment', 'decrement', 'remove'])

const itemTotal = computed(() => {
  const productTotal = props.item.price * props.item.quantity
  const modifiersTotal = props.item.modifiers?.reduce((sum, mod) => {
    return sum + (mod.price * mod.quantity * props.item.quantity)
  }, 0) || 0
  return productTotal + modifiersTotal
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}
</script>