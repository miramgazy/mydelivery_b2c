<template>
  <div 
    class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm overflow-hidden cursor-pointer transition-all hover:shadow-lg border border-gray-100 dark:border-gray-700"
    :class="{ 'opacity-50': !product.is_available || product.is_in_stop_list }"
    @click="handleClick"
  >
    <div class="flex items-stretch p-3 gap-4">
      <!-- Изображение (ровно 20%) -->
      <div class="w-[20%] aspect-square bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden flex-shrink-0 relative">
        <img 
          v-if="product.image_url" 
          :src="product.image_url" 
          :alt="product.product_name"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>

        <!-- Badges on image -->
        <div class="absolute top-1 right-1 flex flex-col gap-1">
          <div v-if="product.has_modifiers" class="w-2 h-2 bg-primary-500 rounded-full shadow-sm" title="С выбором"></div>
          <div v-if="!product.is_available || product.is_in_stop_list" class="w-2 h-2 bg-red-500 rounded-full shadow-sm" title="Недоступно"></div>
        </div>
      </div>

      <!-- Информация (80%) -->
      <div class="flex-1 flex flex-col justify-between py-0.5">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white mb-0.5 text-sm line-clamp-2 leading-tight">
            {{ product.product_name }}
          </h3>
          <p v-if="product.description" class="text-[11px] text-gray-500 dark:text-gray-400 line-clamp-1 leading-tight">
            {{ product.description }}
          </p>
        </div>

        <div class="flex items-center justify-between mt-2">
          <div class="flex flex-col">
            <span class="text-base font-bold text-primary-600 dark:text-primary-400">
              {{ formatPrice(product.price) }} ₸
            </span>
            <span v-if="product.measure_unit" class="text-[10px] text-gray-400 dark:text-gray-500">
              {{ product.measure_unit }}
            </span>
          </div>

          <button
            v-if="product.is_available && !product.is_in_stop_list"
            @click.stop="addToCart"
            class="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center gap-1 group"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span class="text-xs font-medium">Добавить</span>
          </button>
          <span v-else class="text-[10px] text-red-500 font-medium">
            Нет в наличии
          </span>
        </div>
      </div>
    </div>

    <!-- Категория (внизу) -->
    <div class="px-3 py-1.5 bg-gray-50/50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-700 flex justify-between items-center">
      <span class="text-[10px] uppercase tracking-wider font-bold text-gray-400 dark:text-gray-500">
        {{ categoryName }}
      </span>
      <span v-if="product.has_modifiers" class="text-[9px] text-primary-500 font-medium bg-primary-50 dark:bg-primary-900/20 px-1.5 rounded-sm">
        С выбором
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'add-to-cart'])

const cartStore = useCartStore()
const productsStore = useProductsStore()
const notificationStore = useNotificationStore()

const categoryName = computed(() => {
  // Категория может быть объектом (из сериализатора) или ID
  if (!props.product.category) {
    return 'Без категории'
  }
  
  // Если категория - это объект с subgroup_name
  if (typeof props.product.category === 'object' && props.product.category.subgroup_name) {
    return props.product.category.subgroup_name
  }
  
  // Если категория - это ID, ищем в списке категорий
  const categoryId = typeof props.product.category === 'object' 
    ? props.product.category.subgroup_id 
    : props.product.category
    
  const category = productsStore.categories.find(c => c.subgroup_id === categoryId)
  return category ? category.subgroup_name : 'Без категории'
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}

const handleClick = () => {
  if (props.product.is_available && !props.product.is_in_stop_list) {
    emit('click', props.product)
  }
}

const addToCart = () => {
  if (props.product.has_modifiers) {
    emit('add-to-cart', props.product)
  } else {
    try {
      cartStore.addItem(props.product)
      telegramService.vibrate('light')
      notificationStore.show(`${props.product.product_name} добавлен в корзину`)
    } catch (error) {
      telegramService.showAlert(error.message || 'Не удалось добавить товар в корзину')
    }
  }
}
</script>