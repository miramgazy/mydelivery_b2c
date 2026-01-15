import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useOrdersStore = defineStore('orders', () => {
    // State
    const orders = ref([])
    const paymentTypes = ref([])
    const currentOrder = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const pendingOrders = computed(() => {
        return orders.value.filter(o => o.status === 'pending' || o.status === 'confirmed')
    })

    const completedOrders = computed(() => {
        return orders.value.filter(o => o.status === 'completed')
    })

    const activeOrders = computed(() => {
        return orders.value.filter(o =>
            ['pending', 'confirmed', 'preparing', 'delivering'].includes(o.status)
        )
    })

    // Actions

    /**
     * Загрузить заказы пользователя
     */
    async function fetchMyOrders() {
        loading.value = true
        error.value = null

        try {
            const response = await api.get('/orders/my_orders/')
            orders.value = response.data.results || response.data
        } catch (err) {
            console.error('Fetch orders error:', err)
            error.value = 'Не удалось загрузить заказы'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Загрузить все заказы (для админа)
     */
    async function fetchOrders() {
        loading.value = true
        error.value = null

        try {
            const response = await api.get('/orders/')
            orders.value = response.data.results || response.data
        } catch (err) {
            console.error('Fetch orders error:', err)
            error.value = 'Не удалось загрузить заказы'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Получить детали заказа
     */
    async function fetchOrderDetail(orderId) {
        loading.value = true
        error.value = null

        try {
            const response = await api.get(`/orders/${orderId}/`)
            currentOrder.value = response.data
            return response.data
        } catch (err) {
            console.error('Fetch order detail error:', err)
            error.value = 'Не удалось загрузить заказ'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Создать заказ
     */
    async function createOrder(orderData) {
        loading.value = true
        error.value = null

        try {
            const response = await api.post('/orders/', orderData)

            // Добавляем в список
            orders.value.unshift(response.data)
            currentOrder.value = response.data

            return response.data
        } catch (err) {
            console.error('Create order error:', err)
            error.value = err.response?.data?.error || 'Не удалось создать заказ'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Отменить заказ
     */
    async function cancelOrder(orderId) {
        loading.value = true
        error.value = null

        try {
            const response = await api.post(`/orders/${orderId}/cancel/`)

            // Обновляем в списке
            const index = orders.value.findIndex(o => o.order_id === orderId)
            if (index !== -1) {
                orders.value[index] = response.data
            }

            return response.data
        } catch (err) {
            console.error('Cancel order error:', err)
            error.value = 'Не удалось отменить заказ'
            throw err
        } finally {
            loading.value = false
        }
    }

    const lastStatusCheck = ref({}) // { orderId: timestamp }

    /**
     * Получить статус заказа из iiko
     */
    async function fetchOrderStatus(orderId) {
        loading.value = true
        error.value = null

        try {
            const response = await api.get(`/orders/${orderId}/status/`)
            const updatedOrder = response.data.order

            // Обновляем текущий заказ если это он
            if (currentOrder.value && currentOrder.value.order_id === orderId) {
                currentOrder.value = updatedOrder
            }

            // Обновляем в списке
            const index = orders.value.findIndex(o => o.order_id === orderId)
            if (index !== -1) {
                orders.value[index] = updatedOrder
            }

            // Сохраняем время проверки
            lastStatusCheck.value[orderId] = Date.now()

            return response.data
        } catch (err) {
            console.error('Fetch order status error:', err)
            error.value = 'Не удалось получить статус заказа'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Загрузить типы оплаты для организации
     */
    async function fetchPaymentTypes(organizationId) {
        if (!organizationId) return

        try {
            const response = await api.get('/payment-types/', {
                params: { organization: organizationId, is_active: true }
            })
            paymentTypes.value = response.data.results || response.data
            return paymentTypes.value
        } catch (err) {
            console.error('Fetch payment types error:', err)
            throw err
        }
    }

    /**
     * Очистить текущий заказ
     */
    function clearCurrentOrder() {
        currentOrder.value = null
    }

    return {
        // State
        orders,
        currentOrder,
        loading,
        error,
        paymentTypes,

        // Getters
        pendingOrders,
        completedOrders,
        activeOrders,

        // Actions
        fetchMyOrders,
        fetchOrders,
        fetchOrderDetail,
        createOrder,
        cancelOrder,
        fetchOrderStatus,
        fetchPaymentTypes,
        clearCurrentOrder,
        lastStatusCheck
    }
})