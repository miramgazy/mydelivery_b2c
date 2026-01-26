<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
    <!-- Заголовок -->
    <div class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-20">
      <div class="p-4">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Меню
        </h1>

        <!-- Поиск -->
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск блюд..."
            class="w-full px-4 py-3 pl-11 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <svg class="absolute left-3 top-3.5 w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      <!-- Категории -->
      <CategoryList
        :categories="categories"
        :selected-category="selectedCategory"
        @select="handleCategorySelect"
      />
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full"></div>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="p-4">
      <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-center">
        <p class="text-red-800 dark:text-red-200">{{ error }}</p>
        <button
          @click="refresh"
          class="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
        >
          Повторить
        </button>
      </div>
    </div>

    <!-- Список продуктов -->
    <div v-else-if="availableProducts.length > 0" class="p-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ProductCard
          v-for="product in availableProducts"
          :key="product.product_id"
          :product="product"
          @click="showProductDetail"
          @add-to-cart="showProductDetailForModifiers"
        />
      </div>
    </div>

    <!-- Пустое состояние -->
    <div v-else class="flex flex-col items-center justify-center py-20 px-4">
      <svg class="w-24 h-24 text-gray-300 dark:text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-gray-500 dark:text-gray-400 text-lg mb-2">
        {{ searchQuery ? 'Ничего не найдено' : 'Меню пусто' }}
      </p>
      <p class="text-gray-400 dark:text-gray-500 text-sm text-center">
        {{ searchQuery ? 'Попробуйте изменить запрос' : 'Блюда появятся позже' }}
      </p>
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="mt-4 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
      >
        Очистить поиск
      </button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import CategoryList from '@/components/menu/CategoryList.vue'
import ProductCard from '@/components/menu/ProductCard.vue'
import CartButton from '@/components/cart/CartButton.vue'
import CartSheet from '@/components/cart/CartSheet.vue'
import ProductDetailModal from '@/components/menu/ProductDetailModal.vue'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'

const productsStore = useProductsStore()
const cartStore = useCartStore()
const notificationStore = useNotificationStore()

const cartOpen = ref(false)
const productModalOpen = ref(false)
const selectedProduct = ref(null)
const searchQuery = ref('')

const categories = computed(() => productsStore.categories)
const availableProducts = computed(() => productsStore.availableProducts)
const selectedCategory = computed(() => productsStore.selectedCategory)
const loading = computed(() => productsStore.loading)
const error = computed(() => productsStore.error)

// Watch для поиска
watch(searchQuery, (value) => {
  productsStore.setSearchQuery(value)
})

const handleCategorySelect = (categoryId) => {
  productsStore.setSelectedCategory(categoryId)
}

const clearSearch = () => {
  searchQuery.value = ''
  productsStore.clearFilters()
}

const showProductDetail = (product) => {
  selectedProduct.value = product
  productModalOpen.value = true
}

const showProductDetailForModifiers = (product) => {
  selectedProduct.value = product
  productModalOpen.value = true
}

const closeProductModal = () => {
  productModalOpen.value = false
  setTimeout(() => {
    selectedProduct.value = null
  }, 300)
}

const addToCart = (product, modifiers) => {
  try {
    cartStore.addItem(product, modifiers)
    closeProductModal()
    
    telegramService.vibrate('success')
    notificationStore.show(`${product.product_name} добавлен в корзину`)
  } catch (error) {
    telegramService.showAlert(error.message || 'Не удалось добавить товар в корзину')
  }
}

const refresh = async () => {
  try {
    await productsStore.refresh()
  } catch (err) {
    console.error('Refresh error:', err)
  }
}

onMounted(async () => {
  try {
    await productsStore.refresh()
    
    // Показываем кнопку "Назад" в Telegram
    telegramService.showBackButton(() => {
      window.history.back()
    })
  } catch (err) {
    console.error('Mount error:', err)
  }
})
</script>