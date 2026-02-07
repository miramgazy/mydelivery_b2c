<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div 
      class="fixed inset-0 bg-black/60 transition-opacity"
      @click="close"
    ></div>

    <!-- Modal -->
    <div class="relative w-full max-w-lg bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Close Button -->
      <button 
        @click="close"
        class="absolute top-4 right-4 z-10 w-8 h-8 flex items-center justify-center bg-black/20 hover:bg-black/30 text-white rounded-full transition-colors backdrop-blur-sm"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Image: высокая рамка под загруженное фото -->
      <div class="relative w-full aspect-[4/3] min-h-[280px] max-h-[58vh] bg-gray-200 dark:bg-gray-700 shrink-0">
        <img 
          v-if="product.image_url" 
          :src="product.image_url" 
          :alt="product.product_name"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center">
          <svg class="w-16 h-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      </div>

      <!-- Content -->
      <div class="p-6 flex-1 overflow-y-auto">
        <div class="flex justify-between items-start mb-2">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ product.product_name }}</h2>
        </div>
        
        <p v-if="product.description" class="text-gray-600 dark:text-gray-300 mb-6">
            {{ product.description }}
        </p>

        <!-- Modifiers: обязательные показываем как «включено», опциональные — выбор -->
        <div v-if="product.modifiers && product.modifiers.length > 0" class="space-y-4 mb-6">
            <h3 class="font-semibold text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-700 pb-2">Дополнительно</h3>

            <!-- Обязательные (is_required): только отображение, не редактируются -->
            <div
                v-for="mod in requiredModifiers"
                :key="'req-' + mod.modifier_id"
                class="flex items-center justify-between py-1 text-gray-600 dark:text-gray-400"
            >
                <div>
                    <p class="font-medium">{{ mod.modifier_name }}</p>
                    <p v-if="mod.price > 0" class="text-sm">+{{ formatPrice(mod.price) }} ₸ (включено)</p>
                    <p v-else class="text-sm">включено</p>
                </div>
            </div>

            <!-- Опциональные: список выбора, передаём на бэкенд -->
            <div
                v-for="mod in optionalModifiers"
                :key="mod.modifier_id"
                class="flex items-center justify-between"
            >
                <div>
                    <p class="text-gray-800 dark:text-gray-200 font-medium">{{ mod.modifier_name }}</p>
                    <p v-if="mod.price > 0" class="text-sm text-gray-500">+{{ formatPrice(mod.price) }} ₸</p>
                </div>
                <div class="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                    <button
                        @click="decrementModifier(mod)"
                        class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-white dark:hover:bg-gray-600 transition-colors"
                        :disabled="getModifierQuantity(mod.modifier_id) <= 0"
                        :class="{'opacity-50 cursor-not-allowed': getModifierQuantity(mod.modifier_id) <= 0}"
                    >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                        </svg>
                    </button>
                    <span class="w-8 text-center font-medium">{{ getModifierQuantity(mod.modifier_id) }}</span>
                    <button
                        @click="incrementModifier(mod)"
                        class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-white dark:hover:bg-gray-600 transition-colors"
                        :disabled="getModifierQuantity(mod.modifier_id) >= (mod.max_amount || 10)"
                        :class="{'opacity-50 cursor-not-allowed': getModifierQuantity(mod.modifier_id) >= (mod.max_amount || 10)}"
                    >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <button
            @click="addToCart"
            class="w-full py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2"
          >
            <span>В корзину за {{ formatPrice(totalPrice) }} ₸</span>
          </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  isOpen: Boolean
})

const emit = defineEmits(['close', 'add-to-cart'])

const selectedModifiers = ref({})

// Обязательные (is_required === true): скрыты из выбора, добавляются на бэкенде
const requiredModifiers = computed(() => {
  const mods = props.product?.modifiers || []
  return mods.filter(m => m.is_required === true)
})

// Опциональные: отображаем как список выбора, передаём выбранные ID на бэкенд
const optionalModifiers = computed(() => {
  const mods = props.product?.modifiers || []
  return mods.filter(m => m.is_required !== true)
})

watch(() => props.product, () => {
  selectedModifiers.value = {}
}, { immediate: true })

watch(() => props.isOpen, (newVal) => {
  if (newVal) selectedModifiers.value = {}
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}

const getModifierQuantity = (modifierId) => {
  return selectedModifiers.value[modifierId] || 0
}

const incrementModifier = (modifier) => {
  if (!selectedModifiers.value[modifier.modifier_id]) {
    selectedModifiers.value[modifier.modifier_id] = 0
  }
  selectedModifiers.value[modifier.modifier_id]++
}

const decrementModifier = (modifier) => {
  if (selectedModifiers.value[modifier.modifier_id] > 0) {
    selectedModifiers.value[modifier.modifier_id]--
    if (selectedModifiers.value[modifier.modifier_id] === 0) {
      delete selectedModifiers.value[modifier.modifier_id]
    }
  }
}

const totalPrice = computed(() => {
  let price = parseFloat(props.product?.price) || 0
  const mods = props.product?.modifiers || []
  // Обязательные: учитываем в сумме (min_amount или 1)
  requiredModifiers.value.forEach(mod => {
    const qty = Math.max(1, mod.min_amount || 0)
    price += parseFloat(mod.price || 0) * qty
  })
  // Опциональные: выбранное количество
  optionalModifiers.value.forEach(mod => {
    const qty = selectedModifiers.value[mod.modifier_id] || 0
    if (qty > 0) price += parseFloat(mod.price || 0) * qty
  })
  return price
})

const close = () => {
  emit('close')
}

const addToCart = () => {
  // На бэкенд передаём только выбранные опциональные модификаторы
  const modifiersToAdd = []
  optionalModifiers.value.forEach(mod => {
    const qty = selectedModifiers.value[mod.modifier_id] || 0
    if (qty > 0) {
      modifiersToAdd.push({
        modifier_id: mod.modifier_id,
        modifier_name: mod.modifier_name,
        price: mod.price,
        quantity: qty
      })
    }
  })
  emit('add-to-cart', props.product, modifiersToAdd)
}
</script>
