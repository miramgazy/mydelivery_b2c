<template>
  <div class="flex flex-col min-h-screen pb-24 md:pb-8">
    <header class="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-gray-200">
      <div class="px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-semibold">Корзина</h1>
        <router-link :to="{ path: '/', query: $route.query }" class="text-primary text-sm">Меню</router-link>
      </div>
    </header>

    <main class="flex-1 px-4 py-4">
      <div v-if="!cartStore.items.length" class="flex flex-col items-center justify-center py-16 text-center">
        <svg class="w-16 h-16 text-secondary/30 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="text-secondary/70 mb-2">Корзина пуста</p>
        <router-link
          :to="{ path: '/', query: $route.query }"
          class="px-6 py-2 rounded-main bg-primary text-white font-medium"
        >
          Перейти в меню
        </router-link>
      </div>

      <div v-else>
        <div class="space-y-4">
          <div
            v-for="item in cartStore.items"
            :key="item.key"
            class="flex gap-3 p-3 bg-white rounded-main border border-gray-100"
          >
            <div class="w-16 h-16 rounded-main bg-gray-100 flex-shrink-0 overflow-hidden">
              <img
                v-if="item.product.image_url"
                :src="item.product.image_url"
                :alt="item.product.product_name"
                class="w-full h-full object-cover"
              />
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-medium truncate">{{ item.product.product_name }}</h3>
              <p class="text-primary font-semibold text-sm">{{ formatPrice(item.price) }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="cartStore.updateQuantity(item.key, item.quantity - 1)"
                class="w-8 h-8 rounded-main bg-gray-100 flex items-center justify-center font-bold"
              >
                −
              </button>
              <span class="min-w-[24px] text-center">{{ item.quantity }}</span>
              <button
                @click="cartStore.updateQuantity(item.key, item.quantity + 1)"
                class="w-8 h-8 rounded-main bg-primary text-white flex items-center justify-center font-bold"
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Checkout bar -->
    <div
      v-if="cartStore.items.length"
      class="fixed bottom-16 md:bottom-0 left-0 right-0 md:relative p-4 bg-white border-t border-gray-200 safe-area-bottom"
    >
      <div class="flex items-center justify-between max-w-4xl mx-auto">
        <div>
          <span class="text-secondary/70 text-sm">Итого</span>
          <p class="text-xl font-bold text-primary">{{ formatPrice(cartStore.totalPrice) }}</p>
        </div>
        <router-link
          :to="{ path: '/checkout', query: $route.query }"
          class="px-6 py-3 rounded-main bg-primary text-white font-semibold inline-block"
        >
          Оформить заказ
        </router-link>
      </div>
    </div>

    <!-- Tab bar placeholder for mobile -->
    <div class="md:hidden h-16"></div>
  </div>
</template>

<script setup>
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()

function formatPrice(price) {
  if (!price) return '0 ₸'
  return new Intl.NumberFormat('ru-KZ').format(parseFloat(price)) + ' ₸'
}
</script>
