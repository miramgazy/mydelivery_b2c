import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  const totalCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  function addItem(product, quantity = 1, modifiers = []) {
    const key = `${product.id}-${JSON.stringify(modifiers)}`
    const existing = items.value.find(i => i.key === key)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({
        key,
        product,
        quantity,
        modifiers,
        price: product.price,
      })
    }
  }

  function removeItem(key) {
    items.value = items.value.filter(i => i.key !== key)
  }

  function updateQuantity(key, quantity) {
    const item = items.value.find(i => i.key === key)
    if (item) {
      if (quantity <= 0) {
        removeItem(key)
      } else {
        item.quantity = quantity
      }
    }
  }

  function clear() {
    items.value = []
  }

  return {
    items,
    totalCount,
    totalPrice,
    addItem,
    removeItem,
    updateQuantity,
    clear,
  }
})
