<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-end justify-center sm:items-center p-4 sm:p-0">
    <!-- Backdrop -->
    <div 
      class="fixed inset-0 bg-black/50 transition-opacity"
      @click="close"
    ></div>

    <!-- Sheet -->
    <div 
        class="relative w-full max-w-lg bg-white dark:bg-gray-800 rounded-t-2xl sm:rounded-2xl shadow-xl flex flex-col max-h-[85vh] transition-transform transform"
        :class="{ 'translate-y-0': isOpen, 'translate-y-full': !isOpen }"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Корзина</h2>
        <button 
          @click="close"
          class="p-2 -mr-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Items List -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="cartStore.isEmpty" class="flex flex-col items-center justify-center py-10 text-gray-500">
            <svg class="w-16 h-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p>В корзине пусто</p>
        </div>
        
        <CartItem
          v-for="(item, index) in cartStore.items"
          :key="index"
          :item="item"
          :index="index"
          @increment="cartStore.incrementQuantity"
          @decrement="cartStore.decrementQuantity"
          @remove="cartStore.removeItem"
        />
      </div>

      <!-- Footer -->
      <div v-if="!cartStore.isEmpty" class="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <div class="flex justify-between items-center mb-4 text-lg font-bold">
            <span class="text-gray-900 dark:text-white">Итого:</span>
            <span class="text-primary-600 dark:text-primary-400">{{ formatPrice(cartStore.totalPrice) }} ₸</span>
        </div>
        
        <button
            @click="checkout"
            class="w-full py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-primary-500/30"
        >
            Оформить заказ
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'
import CartItem from './CartItem.vue'
import telegramService from '@/services/telegram'

const props = defineProps({
    isOpen: Boolean
})

const emit = defineEmits(['close'])
const router = useRouter()
const cartStore = useCartStore()

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}

const close = () => {
    emit('close')
}

const checkout = () => {
    telegramService.vibrate('light')
    close()
    router.push('/checkout')
}
</script>
