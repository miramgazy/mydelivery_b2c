<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="p-4">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">{{ t('orders.title') }}</h1>

        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-10">
            <div class="animate-spin w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full"></div>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="bg-red-50 text-red-700 p-4 rounded-xl mb-4">
            {{ error }}
        </div>

        <!-- Empty State -->
        <div v-else-if="orders.length === 0" class="text-center py-10">
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p class="text-gray-500 text-lg">{{ t('orders.empty') }}</p>
            <router-link to="/menu" class="inline-block mt-4 text-primary-600 font-medium">{{ t('orders.goToMenu') }}</router-link>
        </div>

        <!-- Orders List -->
        <div v-else class="space-y-4">
            <div 
                v-for="order in orders" 
                :key="getOrderId(order)"
                @click="$router.push(`/orders/${getOrderId(order)}`)"
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow p-4 cursor-pointer"
            >
                <div class="flex justify-between items-start mb-3">
                    <div>
                         <p class="font-bold text-lg text-gray-900 dark:text-white">{{ t('orders.order') }} #{{ order.order_number || String(getOrderId(order)).substring(0, 8).toUpperCase() }}</p>
                         <p class="text-xs text-gray-500">{{ formatDate(order.created_at) }}</p>
                    </div>
                    <span 
                        class="px-3 py-1 rounded-full text-xs font-bold"
                        :class="getStatusColor(order.status)"
                    >
                        {{ order.status_display }}
                    </span>
                </div>
                
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-600 dark:text-gray-400">
                        {{ order.items_count || (order.items ? order.items.length : 0) }} {{ t('orders.positions') }}
                    </span>
                    <span class="font-bold text-gray-900 dark:text-white">
                        {{ formatPrice(order.total_amount) }} ₸
                    </span>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useOrdersStore } from '@/stores/orders'
import { format, parseISO, isValid } from 'date-fns'
import { ru } from 'date-fns/locale'

const { t } = useI18n()
const ordersStore = useOrdersStore()

const orders = computed(() => ordersStore.orders)
const loading = computed(() => ordersStore.loading)
const error = computed(() => ordersStore.error)

const getOrderId = (order) => order?.order_id || order?.id

const normalizeIsoDate = (dateString) => {
    // Safari/iOS can choke on microseconds; keep only milliseconds
    return String(dateString).replace(/\.(\d{3})\d+/, '.$1')
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    const normalized = normalizeIsoDate(dateString)
    const parsed = parseISO(normalized)
    const d = isValid(parsed) ? parsed : new Date(normalized)
    if (!isValid(d)) return ''
    return format(d, 'd MMMM yyyy, HH:mm', { locale: ru })
}

const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-KZ').format(price)
}

const getStatusColor = (status) => {
    switch (status) {
        case 'pending': return 'bg-gray-100 text-gray-800'
        case 'confirmed': return 'bg-blue-100 text-blue-800'
        case 'preparing': return 'bg-yellow-100 text-yellow-800'
        case 'delivering': return 'bg-purple-100 text-purple-800'
        case 'completed': return 'bg-green-100 text-green-800'
        case 'cancelled': return 'bg-red-100 text-red-800'
        default: return 'bg-gray-100 text-gray-800'
    }
}

onMounted(() => {
    ordersStore.fetchMyOrders()
})
</script>
