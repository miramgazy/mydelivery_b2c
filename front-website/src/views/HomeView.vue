<template>
  <div class="flex flex-col min-h-screen pb-20 md:pb-0">
    <!-- Header -->
    <header class="sticky top-0 z-40 bg-background/95 backdrop-blur border-b border-gray-200">
      <div class="px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="flex-1 flex items-center gap-2 bg-gray-100 rounded-main px-3 py-2 min-h-[40px]">
            <svg class="w-4 h-4 text-secondary/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="text-sm text-secondary/80 truncate">
              {{ organization?.city || 'Выберите адрес' }}
            </span>
          </div>
          <div class="flex-1 relative">
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Поиск блюд..."
              class="w-full rounded-main border border-gray-200 px-3 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <router-link
            :to="{ path: '/profile', query: $route.query }"
            class="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center"
          >
            <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
        </div>
      </div>
    </header>

    <!-- Categories - Sticky horizontal scroll -->
    <div class="sticky top-[57px] z-30 bg-background border-b border-gray-100 overflow-x-auto scrollbar-hide">
      <div class="flex gap-2 px-4 py-3 min-w-max">
        <button
          v-for="cat in categories"
          :key="cat.subgroup_id"
          @click="websiteStore.setSelectedCategory(selectedCategory === cat.subgroup_id ? null : cat.subgroup_id)"
          :class="[
            'px-4 py-2 rounded-main text-sm font-medium whitespace-nowrap transition-colors',
            selectedCategory === cat.subgroup_id
              ? 'bg-primary text-white'
              : 'bg-gray-100 text-secondary hover:bg-gray-200'
          ]"
        >
          {{ cat.subgroup_name }}
        </button>
      </div>
    </div>

    <!-- Products Grid -->
    <main class="flex-1 px-4 py-4">
      <div v-if="websiteStore.loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent"></div>
      </div>
      <div v-else-if="!availableProducts.length" class="text-center py-12 text-secondary/70">
        Блюда не найдены
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div
          v-for="product in availableProducts"
          :key="product.id"
          class="bg-white rounded-main border border-gray-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="aspect-[4/3] bg-gray-100 relative overflow-hidden">
            <img
              v-if="product.image_url"
              :src="product.image_url"
              :alt="product.product_name"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-secondary/30">
              <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14" />
              </svg>
            </div>
          </div>
          <div class="p-3">
            <h3 class="font-medium text-secondary line-clamp-2 mb-1">{{ product.product_name }}</h3>
            <div class="flex items-center justify-between">
              <span class="text-primary font-semibold">{{ formatPrice(product.price) }}</span>
              <div class="flex items-center gap-1">
                <button
                  v-if="getQuantity(product) > 0"
                  @click="decrementProduct(product)"
                  class="w-8 h-8 rounded-main bg-primary/20 text-primary flex items-center justify-center font-bold"
                >
                  −
                </button>
                <span v-if="getQuantity(product) > 0" class="min-w-[24px] text-center font-medium">
                  {{ getQuantity(product) }}
                </span>
                <button
                  @click="incrementProduct(product)"
                  class="w-8 h-8 rounded-main bg-primary text-white flex items-center justify-center font-bold hover:opacity-90"
                >
                  +
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Mobile Tab Bar -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom z-50">
      <div class="flex justify-around py-2">
        <router-link
          :to="{ path: '/', query: $route.query }"
          class="flex flex-col items-center gap-1 px-6 py-2 rounded-main"
          :class="isActive('menu') ? 'text-primary' : 'text-secondary/60'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span class="text-xs">Меню</span>
        </router-link>
        <router-link
          :to="{ path: '/cart', query: $route.query }"
          class="flex flex-col items-center gap-1 px-6 py-2 rounded-main relative"
          :class="isActive('cart') ? 'text-primary' : 'text-secondary/60'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span class="text-xs">Корзина</span>
          <span
            v-if="cartStore.totalCount > 0"
            class="absolute -top-1 -right-2 min-w-[18px] h-[18px] rounded-full bg-primary text-white text-xs flex items-center justify-center"
          >
            {{ cartStore.totalCount }}
          </span>
        </router-link>
        <router-link
          :to="{ path: '/profile', query: $route.query }"
          class="flex flex-col items-center gap-1 px-6 py-2 rounded-main"
          :class="isActive('profile') ? 'text-primary' : 'text-secondary/60'"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="text-xs">Профиль</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useWebsiteStore } from '@/stores/website'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const websiteStore = useWebsiteStore()
const cartStore = useCartStore()

const organization = computed(() => websiteStore.organization)
const categories = computed(() => websiteStore.categories)
const selectedCategory = computed(() => websiteStore.selectedCategory)
const availableProducts = computed(() => websiteStore.availableProducts)
const searchQuery = computed({
  get: () => websiteStore.searchQuery,
  set: (v) => websiteStore.setSearchQuery(v),
})

function isActive(tab) {
  return route.meta?.tab === tab
}

function formatPrice(price) {
  if (!price) return '0 ₸'
  return new Intl.NumberFormat('ru-KZ').format(parseFloat(price)) + ' ₸'
}

function getQuantity(product) {
  const item = cartStore.items.find(i => i.product.id === product.id)
  return item?.quantity || 0
}

function incrementProduct(product) {
  cartStore.addItem(product, 1)
}

function decrementProduct(product) {
  const item = cartStore.items.find(i => i.product.id === product.id)
  if (item && item.quantity > 1) {
    cartStore.updateQuantity(item.key, item.quantity - 1)
  } else if (item) {
    cartStore.removeItem(item.key)
  }
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
