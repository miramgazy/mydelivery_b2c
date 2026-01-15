<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-4 sticky top-0 z-20">
        <button @click="$router.back()" class="p-2 -ml-2 hover:bg-gray-100 rounded-full">
             <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
        </button>
        <h1 class="text-xl font-bold">Оформление заказа</h1>
    </div>

    <div v-if="adminWarning" class="p-6 text-center space-y-4">
        <div class="w-20 h-20 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto">
            <svg class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">Информация не полная</h2>
        <p class="text-gray-600 dark:text-gray-400">
            {{ adminWarning }}
            Пожалуйста, обратитесь к администратору для дополнения информации.
        </p>
        <button @click="$router.push('/')" class="w-full py-3 bg-primary-600 text-white font-bold rounded-xl">
            Вернуться в меню
        </button>
    </div>

    <div v-else class="p-4 space-y-6">
        <!-- Items Preview -->
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm">
            <h3 class="font-bold mb-2">Ваш заказ</h3>
            <div class="space-y-2 mb-4">
                <div v-for="item in cartStore.items" :key="item.product_id" class="flex justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">{{ item.quantity }}x {{ item.product_name }}</span>
                    <span>{{ formatPrice(item.price * item.quantity) }} ₸</span>
                </div>
            </div>
            <div class="flex justify-between items-center text-lg font-bold border-t pt-2 border-gray-100 dark:border-gray-700">
                <span>Итого:</span>
                <span class="text-primary-600">{{ formatPrice(cartStore.totalPrice) }} ₸</span>
            </div>
        </div>

        <!-- Phone -->
        <div class="space-y-2">
            <label class="font-semibold text-gray-700 dark:text-gray-300">Номер телефона</label>
            <input 
                v-model="form.phone"
                type="tel"
                placeholder="+7 (___) ___-__-__"
                class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 outline-none"
            />
        </div>

        <!-- Delivery Type -->
        <div class="space-y-2">
            <label class="font-semibold text-gray-700 dark:text-gray-300">Способ получения</label>
            <div class="grid grid-cols-2 gap-3">
                <button 
                    @click="form.deliveryType = 'delivery'"
                    class="p-3 rounded-xl border-2 transition-all text-center font-medium"
                    :class="form.deliveryType === 'delivery' ? 'border-primary-600 bg-primary-50 text-primary-700' : 'border-gray-200 bg-white text-gray-600'"
                >
                    Доставка
                </button>
                 <button 
                    @click="form.deliveryType = 'pickup'"
                    class="p-3 rounded-xl border-2 transition-all text-center font-medium"
                    :class="form.deliveryType === 'pickup' ? 'border-primary-600 bg-primary-50 text-primary-700' : 'border-gray-200 bg-white text-gray-600'"
                >
                    Самовывоз
                </button>
            </div>
        </div>

        <!-- Address Selection (if delivery) -->
        <div v-if="form.deliveryType === 'delivery'" class="space-y-3">
             <label class="font-semibold text-gray-700 dark:text-gray-300">Адрес доставки</label>
             
             <!-- Saved Addresses -->
             <div v-if="authStore.user?.addresses?.length > 0" class="space-y-2">
                <div 
                    v-for="addr in authStore.user.addresses" 
                    :key="addr.id"
                    @click="form.delivery_address_id = addr.id"
                    class="p-3 rounded-xl border-2 cursor-pointer transition-all"
                    :class="form.delivery_address_id === addr.id ? 'border-primary-600 bg-primary-50' : 'border-gray-100 bg-white dark:bg-gray-800 dark:border-gray-700'"
                >
                    <div class="flex items-center gap-3">
                        <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center" :class="form.delivery_address_id === addr.id ? 'border-primary-600' : 'border-gray-300'">
                            <div v-if="form.delivery_address_id === addr.id" class="w-2.5 h-2.5 bg-primary-600 rounded-full"></div>
                        </div>
                        <span class="text-sm">{{ addr.full_address }}</span>
                    </div>
                </div>
                <!-- Option to enter manually if needed, but for now lets keep it simple -->
             </div>

             <div v-else class="p-4 bg-orange-50 text-orange-700 rounded-xl text-sm">
                 У вас нет сохраненных адресов. Пожалуйста, добавьте адрес в профиле.
                 <button @click="$router.push('/profile')" class="block mt-2 font-bold underline">Перейти в профиль</button>
             </div>

             <textarea 
                v-model="form.comment"
                placeholder="Комментарий к заказу (код домофона и т.д.)"
                rows="2"
                class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 outline-none"
            ></textarea>
        </div>

        <!-- Payment Method (only if payment types are configured) -->
        <div v-if="ordersStore.paymentTypes.length > 0" class="space-y-2">
            <label class="font-semibold text-gray-700 dark:text-gray-300">Способ оплаты</label>
            <select 
                v-model="form.payment_type_id"
                class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 outline-none"
            >
                <option :value="null" disabled>Выберите способ оплаты</option>
                <option 
                    v-for="pt in ordersStore.paymentTypes" 
                    :key="pt.payment_id" 
                    :value="pt.payment_id"
                >
                    {{ pt.payment_name }}
                </option>
            </select>
        </div>

        <!-- Terminal Selection (if multiple) -->
        <div v-if="authStore.user?.terminals?.length > 1" class="space-y-2">
            <label class="font-semibold text-gray-700 dark:text-gray-300">Выберите филиал</label>
            <select 
                v-model="form.terminal_id"
                class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 outline-none"
                required
            >
                <option :value="null" disabled>Выберите терминал</option>
                <option 
                    v-for="terminal in authStore.user.terminals" 
                    :key="terminal.terminal_id" 
                    :value="terminal.terminal_id"
                >
                    {{ terminal.terminal_group_name }}
                </option>
            </select>
        </div>

         <!-- Submit -->
         <button 
            @click="submitOrder"
            :disabled="loading || !!adminWarning"
            class="w-full py-4 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-bold rounded-xl shadow-lg transition-transform active:scale-95 flex items-center justify-center gap-2"
        >
            <span v-if="loading" class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></span>
            <span v-else>Подтвердить заказ</span>
         </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useOrdersStore } from '@/stores/orders'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'
import { useNotificationStore } from '@/stores/notifications'

const router = useRouter()
const cartStore = useCartStore()
const ordersStore = useOrdersStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const loading = ref(false)
const dataLoaded = ref(false)

const form = reactive({
    phone: '',
    deliveryType: 'delivery',
    delivery_address_id: null,
    comment: '',
    payment_type_id: null,
    terminal_id: null
})

// Validation for system-level data
const adminWarning = computed(() => {
    if (!dataLoaded.value) return null
    
    if (!authStore.user?.organization) {
        return 'Ваш профиль не привязан к организации.'
    }
    if (!authStore.user?.terminals || authStore.user.terminals.length === 0) {
        return 'Для вашей организации не настроены торговые точки.'
    }
    return null
})

onMounted(async () => {
    if (authStore.user) {
        form.phone = authStore.user.phone || '+7'
        
        // Load payment types
        try {
            await ordersStore.fetchPaymentTypes(authStore.user.organization)
            
            // Set default payment type if available
            if (ordersStore.paymentTypes.length > 0) {
                form.payment_type_id = ordersStore.paymentTypes[0].payment_id
            }
        } catch (e) {
            console.error('Failed to load payment types', e)
        }

        // Set default terminal if only one
        if (authStore.user.terminals?.length === 1) {
            form.terminal_id = authStore.user.terminals[0].terminal_id
        }

        // Set default address if available
        const defaultAddr = authStore.user.addresses?.find(a => a.is_default) || authStore.user.addresses?.[0]
        if (defaultAddr) {
            form.delivery_address_id = defaultAddr.id
        }
    }
    dataLoaded.value = true
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-KZ').format(price)
}

const submitOrder = async () => {
    // Validation
    if (!form.phone || form.phone.length < 10) {
        telegramService.showAlert('Введите корректный номер телефона')
        return
    }
    if (form.deliveryType === 'delivery' && !form.delivery_address_id) {
        telegramService.showAlert('Укажите адрес доставки')
        return
    }
    // Payment type is optional - only validate if payment types are configured
    if (ordersStore.paymentTypes.length > 0 && !form.payment_type_id) {
        telegramService.showAlert('Выберите способ оплаты')
        return
    }
    if (authStore.user?.terminals?.length > 1 && !form.terminal_id) {
        telegramService.showAlert('Выберите филиал для заказа')
        return
    }

    loading.value = true
    try {
        const orderData = {
            items: cartStore.getOrderData(),
            phone: form.phone,
            comment: form.comment,
            payment_type_id: form.payment_type_id,
            terminal_id: form.terminal_id,
            delivery_address_id: form.deliveryType === 'delivery' ? form.delivery_address_id : null
        }

        await ordersStore.createOrder(orderData)

        cartStore.clearCart()
        notificationStore.show('Заказ успешно создан!')
        router.push('/orders')
    } catch (e) {
        const msg = e.response?.data?.error || e.response?.data?.detail || e.message
        telegramService.showAlert('Ошибка при создании заказа: ' + msg)
    } finally {
        loading.value = false
    }
}
</script>
