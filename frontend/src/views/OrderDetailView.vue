<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-20 px-4 py-4 flex items-center gap-4">
        <button @click="$router.back()" class="p-2 -ml-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
            <svg class="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
        </button>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">Детали заказа</h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full"></div>
    </div>
    
    <!-- Error -->
    <div v-else-if="error" class="p-4 text-center">
        <p class="text-red-600">{{ error }}</p>
    </div>

    <!-- Content -->
    <div v-else-if="order" class="p-4 space-y-4">
        <!-- Status Card -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm text-center">
            <h2 class="text-gray-500 text-sm mb-1">Заказ #{{ order.order_number || String(getOrderId(order)).substring(0, 8).toUpperCase() }}</h2>
            <div class="text-3xl font-bold text-primary-600 mb-2">{{ order.status_display }}</div>
            <p class="text-xs text-gray-400">{{ formatDate(order.created_at) }}</p>
        </div>

        <!-- Items -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm">
            <h3 class="font-bold text-lg mb-4 text-gray-900 dark:text-white">Состав заказа</h3>
            <div class="space-y-4">
                <div v-for="item in order.items" :key="item.id" class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                    <div class="flex-1">
                        <p class="font-medium text-gray-900 dark:text-white">{{ item.product_name }}</p>
                        <p class="text-sm text-gray-500">{{ item.quantity }} x {{ formatPrice(item.price) }} ₸</p>
                        
                        <!-- Modifiers -->
                        <div v-if="item.modifiers && item.modifiers.length" class="mt-1 ml-2 space-y-1">
                            <p v-for="mod in item.modifiers" :key="mod.id" class="text-xs text-gray-400">
                                + {{ mod.modifier_name }} <span v-if="mod.quantity > 1">x {{mod.quantity}}</span>
                            </p>
                        </div>
                    </div>
                    <div class="text-right font-semibold text-gray-900 dark:text-white">
                        {{ formatPrice(item.total_price) }} ₸
                    </div>
                </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 space-y-2">
                <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Товары:</span>
                    <span>{{ formatPrice(order.total_amount) }} ₸</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">Доставка:</span>
                    <span class="font-medium">
                        {{ order.delivery_cost != null && Number(order.delivery_cost) > 0 ? formatPrice(order.delivery_cost) + ' ₸' : 'Бесплатно' }}
                    </span>
                </div>
                <div class="flex justify-between items-center text-xl font-bold pt-2 border-t border-gray-100 dark:border-gray-700">
                    <span>Итого:</span>
                    <span>{{ formatPrice((Number(order.total_amount) || 0) + (Number(order.delivery_cost) || 0)) }} ₸</span>
                </div>
            </div>
        </div>

        <!-- Info -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm space-y-3">
            <h3 class="font-bold text-lg mb-2 text-gray-900 dark:text-white">Информация</h3>
            
            <div class="flex justify-between text-sm">
                <span class="text-gray-500">Адрес доставки:</span>
                <span class="font-medium text-right max-w-[60%]">{{ order.delivery_address_full || 'Самовывоз / Не указан' }}</span>
            </div>
             <div class="flex justify-between text-sm">
                <span class="text-gray-500">Телефон:</span>
                <span class="font-medium">{{ order.phone }}</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-gray-500">Оплата:</span>
                <span class="font-medium">{{ order.payment_type_name || 'Не указана' }}</span>
            </div>
             <div v-if="order.comment" class="flex flex-col text-sm mt-2">
                <span class="text-gray-500 mb-1">Комментарий:</span>
                <span class="font-medium bg-gray-50 p-2 rounded">{{ order.comment }}</span>
            </div>
        </div>

        <!-- Iiko Info -->
        <div v-if="order.iiko_delivery_number" class="bg-primary-50 dark:bg-primary-900/20 p-4 rounded-xl border border-primary-100 dark:border-primary-800">
            <div class="flex justify-between items-center">
                <span class="text-primary-800 dark:text-primary-200 text-sm font-medium">Номер доставки iiko:</span>
                <span class="text-primary-900 dark:text-primary-100 font-bold">{{ order.iiko_delivery_number }}</span>
            </div>
        </div>

        <!-- Check Status Button -->
        <button 
            v-if="!['completed', 'cancelled'].includes(order.status)"
            @click="handleCheckStatus"
            :disabled="statusCheckDisabled"
            class="w-full py-3 bg-white dark:bg-gray-800 text-primary-600 font-semibold rounded-xl border border-primary-200 dark:border-primary-800 hover:bg-primary-50 transition-colors disabled:opacity-50 disabled:bg-gray-50 flex flex-col items-center gap-1"
        >
            <span>Проверить статус</span>
            <span v-if="statusCheckDisabled" class="text-[10px] font-normal text-gray-500">
                Будет доступно через {{ remainingTime }}
            </span>
        </button>

        <!-- Cancel Button -->
        <button 
            v-if="['pending', 'confirmed', 'InProgress'].includes(order.status)"
            @click="handleCancel"
            class="w-full py-3 bg-red-100 text-red-700 font-semibold rounded-xl hover:bg-red-200 transition-colors mt-2"
        >
            Отменить заказ
        </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { format, parseISO, isValid } from 'date-fns'
import { ru } from 'date-fns/locale'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'

const route = useRoute()
const ordersStore = useOrdersStore()
const notificationStore = useNotificationStore()
const timer = ref(null)
const now = ref(Date.now())

const order = computed(() => ordersStore.currentOrder)
const loading = computed(() => ordersStore.loading)
const error = computed(() => ordersStore.error)

const getOrderId = (o) => o?.order_id || o?.id

// Rate limiting logic (15 minutes = 900,000 ms)
const CHECK_INTERVAL = 15 * 60 * 1000 
const statusCheckDisabled = computed(() => {
    if (!order.value) return false
    const lastCheck = ordersStore.lastStatusCheck[getOrderId(order.value)]
    if (!lastCheck) return false
    return (now.value - lastCheck) < CHECK_INTERVAL
})

const remainingTime = computed(() => {
    if (!order.value) return ''
    const lastCheck = ordersStore.lastStatusCheck[getOrderId(order.value)]
    if (!lastCheck) return ''
    const diff = CHECK_INTERVAL - (now.value - lastCheck)
    if (diff <= 0) return ''
    
    const minutes = Math.floor(diff / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const formatDate = (dateString) => {
    if (!dateString) return ''
    const normalized = String(dateString).replace(/\.(\d{3})\d+/, '.$1')
    const parsed = parseISO(normalized)
    const d = isValid(parsed) ? parsed : new Date(normalized)
    if (!isValid(d)) return ''
    return format(d, 'd MMMM yyyy, HH:mm', { locale: ru })
}

const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-KZ').format(price)
}

const handleCheckStatus = async () => {
    if (statusCheckDisabled.value) return
    
    try {
        telegramService.vibrate('light')
        await ordersStore.fetchOrderStatus(getOrderId(order.value))
        notificationStore.show('Статус обновлен')
    } catch (e) {
        telegramService.showAlert('Ошибка при обновлении статуса')
    }
}

const handleCancel = () => {
    telegramService.showConfirm('Вы действительно хотите отменить заказ?', async () => {
        try {
            await ordersStore.cancelOrder(getOrderId(order.value))
            notificationStore.show('Заказ отменен')
        } catch (e) {
            telegramService.showAlert('Не удалось отменить заказ')
        }
    })
}

onMounted(() => {
    const orderId = route.params.id
    if (orderId) {
        ordersStore.fetchOrderDetail(orderId)
    }
    
    timer.value = setInterval(() => {
        now.value = Date.now()
    }, 1000)
})

onBeforeUnmount(() => {
    if (timer.value) clearInterval(timer.value)
})
</script>
