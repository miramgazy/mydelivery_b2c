<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-primary-600 pt-8 pb-6 px-4 rounded-b-3xl relative overflow-hidden">
      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-4">
          <button
            @click="$router.back()"
            class="p-2 -ml-2 rounded-full hover:bg-white/10 w-10 h-10 flex items-center justify-center transition-colors"
          >
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 class="text-2xl font-bold text-white flex-1">
            {{ groupName || 'Быстрое меню' }}
          </h1>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mb-4"></div>
      <p class="text-gray-500">Загрузка товаров...</p>
    </div>

    <!-- Products List -->
    <div v-else-if="products.length > 0" class="p-4 space-y-3">
      <ProductCard
        v-for="product in products"
        :key="product.id || product.product_id"
        :product="product"
        @click="showProductDetail"
        @add-to-cart="showProductDetailForModifiers"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-20 px-4">
      <svg class="w-24 h-24 text-gray-300 dark:text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-gray-500 dark:text-gray-400 text-lg mb-2">
        Товары не найдены
      </p>
      <p class="text-gray-400 dark:text-gray-500 text-sm text-center">
        В этой группе пока нет доступных товаров
      </p>
    </div>

    <!-- Кнопка корзины -->
    <CartButton @open="cartOpen = true" />

    <!-- Корзина -->
    <CartSheet :is-open="cartOpen" @close="cartOpen = false" />

    <!-- Модальное окно с деталями продукта -->
    <ProductDetailModal
      v-if="selectedProduct"
      :product="selectedProduct"
      :is-open="productModalOpen"
      @close="closeProductModal"
      @add-to-cart="addToCart"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import fastMenuService from '@/services/fast-menu.service'
import ProductCard from '@/components/menu/ProductCard.vue'
import CartButton from '@/components/cart/CartButton.vue'
import CartSheet from '@/components/cart/CartSheet.vue'
import ProductDetailModal from '@/components/menu/ProductDetailModal.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const cartStore = useCartStore()
const productsStore = useProductsStore()
const authStore = useAuthStore()

const groupId = computed(() => route.params.groupId)
const groupName = computed(() => route.query.name || 'Быстрое меню')
const products = ref([])
const loading = ref(false)
const cartOpen = ref(false)
const productModalOpen = ref(false)
const selectedProduct = ref(null)

onMounted(async () => {
  await loadGroupProducts()
})

const loadGroupProducts = async () => {
  loading.value = true
  try {
    const terminalId = authStore.user?.terminals?.[0]?.terminal_id || authStore.user?.terminals?.[0]?.id || null
    const groups = await fastMenuService.getPublicGroups(terminalId)
    const group = groups.find(g => g.id === groupId.value)
    
    if (group && group.products) {
      products.value = group.products
    } else {
      products.value = []
    }
  } catch (err) {
    console.error('Failed to load group products:', err)
    products.value = []
  } finally {
    loading.value = false
  }
}

const showProductDetail = (product) => {
  selectedProduct.value = product
  productModalOpen.value = true
}

const showProductDetailForModifiers = (product) => {
  showProductDetail(product)
}

const closeProductModal = () => {
  productModalOpen.value = false
  selectedProduct.value = null
}

const addToCart = (product, modifiers = []) => {
  try {
    cartStore.addItem(product, modifiers)
    closeProductModal()
  } catch (error) {
    console.error('Failed to add to cart:', error)
  }
}
</script>
