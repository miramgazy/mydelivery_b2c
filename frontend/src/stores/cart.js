import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
    // State
    const items = ref([])

    // Getters
    const itemsCount = computed(() => {
        return items.value.reduce((total, item) => total + item.quantity, 0)
    })

    const totalPrice = computed(() => {
        return items.value.reduce((total, item) => {
            const itemTotal = item.price * item.quantity
            const modifiersTotal = item.modifiers?.reduce((sum, mod) => {
                return sum + (mod.price * mod.quantity * item.quantity)
            }, 0) || 0
            return total + itemTotal + modifiersTotal
        }, 0)
    })

    const isEmpty = computed(() => items.value.length === 0)

    // Actions

    /**
     * Добавить товар в корзину
     */
    function addItem(product, modifiers = []) {
        // Проверяем, не находится ли продукт в стоп-листе
        if (product.is_in_stop_list) {
            throw new Error(`Продукт "${product.product_name}" временно недоступен`)
        }
        
        if (!product.is_available) {
            throw new Error(`Продукт "${product.product_name}" недоступен`)
        }
        
        const existingItemIndex = items.value.findIndex(item => {
            return item.product_id === product.product_id &&
                JSON.stringify(item.modifiers) === JSON.stringify(modifiers)
        })

        if (existingItemIndex !== -1) {
            // Товар с такими же модификаторами уже есть - увеличиваем количество
            items.value[existingItemIndex].quantity++
        } else {
            // Добавляем новый товар
            items.value.push({
                product_id: product.product_id,
                product_name: product.product_name,
                price: product.price,
                quantity: 1,
                modifiers: modifiers.map(mod => ({
                    modifier_id: mod.modifier_id,
                    modifier_name: mod.modifier_name,
                    quantity: mod.quantity || 1,
                    price: mod.price || 0
                })),
                image_url: product.image_url
            })
        }
    }

    /**
     * Удалить товар из корзины
     */
    function removeItem(index) {
        items.value.splice(index, 1)
    }

    /**
     * Обновить количество товара
     */
    function updateQuantity(index, quantity) {
        if (quantity <= 0) {
            removeItem(index)
        } else {
            items.value[index].quantity = quantity
        }
    }

    /**
     * Увеличить количество
     */
    function incrementQuantity(index) {
        items.value[index].quantity++
    }

    /**
     * Уменьшить количество
     */
    function decrementQuantity(index) {
        if (items.value[index].quantity > 1) {
            items.value[index].quantity--
        } else {
            removeItem(index)
        }
    }

    /**
     * Очистить корзину
     */
    function clearCart() {
        items.value = []
    }

    /**
     * Получить данные для отправки заказа
     */
    function getOrderData() {
        return items.value.map(item => {
            const mods = item.modifiers || []
            return {
                product_id: item.product_id,
                quantity: item.quantity,
                modifiers: mods.length > 0 ? mods.map(mod => ({
                    modifier_id: mod.modifier_id,
                    quantity: mod.quantity
                })) : []
            }
        })
    }

    return {
        // State
        items,

        // Getters
        itemsCount,
        totalPrice,
        isEmpty,

        // Actions
        addItem,
        removeItem,
        updateQuantity,
        incrementQuantity,
        decrementQuantity,
        clearCart,
        getOrderData
    }
})