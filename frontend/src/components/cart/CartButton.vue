<template>
  <button
    v-if="!isEmpty"
    @click="openCart"
    class="fixed bottom-4 right-4 z-50 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg transition-all transform hover:scale-105"
  >
    <div class="flex items-center gap-3 px-6 py-4">
      <!-- Иконка корзины -->
      <div class="relative">
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        
        <!-- Badge с количеством -->
        <span 
          class="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center"
        >
          {{ itemsCount }}
        </span>
      </div>

      <!-- Цена -->
      <div class="flex flex-col items-start">
        <span class="text-xs opacity-90">Корзина</span>
        <span class="text-lg font-bold">{{ formatPrice(totalPrice) }} ₸</span>
      </div>

      <!-- Стрелка -->
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </div>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useCartStore } from '@/stores/cart'
import telegramService from '@/services/telegram'

const emit = defineEmits(['open'])

const cartStore = useCartStore()

const itemsCount = computed(() => cartStore.itemsCount)
const totalPrice = computed(() => cartStore.totalPrice)
const isEmpty = computed(() => cartStore.isEmpty)

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}

const openCart = () => {
  telegramService.vibrate('light')
  emit('open')
}
</script>