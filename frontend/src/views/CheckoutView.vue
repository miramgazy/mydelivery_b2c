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
            <label class="font-semibold text-gray-700 dark:text-gray-300">Номер телефона для связи</label>
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
                
                <button
                  @click="$router.push({ path: '/profile/addresses', query: { return: '/checkout' } })"
                  class="w-full py-3 rounded-xl font-semibold border-2 transition-all"
                  :class="(authStore.user?.addresses?.length || 0) >= 3 ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white dark:bg-gray-800 text-primary-600 border-primary-200 hover:bg-primary-50'"
                  :disabled="(authStore.user?.addresses?.length || 0) >= 3"
                >
                  Добавить другой адрес
                </button>
             </div>

             <div v-else class="p-4 bg-orange-50 text-orange-700 rounded-xl text-sm">
                 У вас нет сохраненных адресов. Пожалуйста, добавьте адрес в профиле.
                 <button @click="$router.push('/profile/addresses')" class="block mt-2 font-bold underline">Добавить адрес</button>
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

            <!-- Remote payment (Kaspi) phone selection -->
            <div
              v-if="selectedPaymentSystemType === 'remote_payment'"
              class="mt-3 space-y-2"
            >
              <p class="text-xs text-gray-600 dark:text-gray-400">
                Счет Kaspi будет выставлен на указанный номер после подтверждения заказа.
              </p>

              <div class="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-xl px-3 py-2">
                <div class="flex flex-col">
                  <span class="text-xs text-gray-500 dark:text-gray-400">Номер для Kaspi</span>
                  <span class="text-sm font-semibold text-gray-900 dark:text-white">
                    {{ remotePaymentPhoneDisplay || 'Не указан' }}
                  </span>
                </div>
                <button
                  type="button"
                  @click="showPhoneSelector = !showPhoneSelector"
                  class="text-xs font-semibold text-primary-600 hover:text-primary-700"
                >
                  Изменить номер
                </button>
              </div>

              <div v-if="showPhoneSelector" class="space-y-3 mt-2">
                <!-- Saved billing phones -->
                <div v-if="billingPhones.length > 0" class="space-y-2">
                  <div
                    v-for="bp in billingPhones"
                    :key="bp.id"
                    @click="selectBillingPhone(bp)"
                    class="flex items-center justify-between px-3 py-2 rounded-xl border-2 cursor-pointer transition-all"
                    :class="bp.id === selectedBillingPhoneId
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 bg-white dark:bg-gray-900 dark:border-gray-700'"
                  >
                    <div class="flex items-center gap-3">
                      <div
                        class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
                        :class="bp.id === selectedBillingPhoneId ? 'border-primary-600' : 'border-gray-300'"
                      >
                        <div
                          v-if="bp.id === selectedBillingPhoneId"
                          class="w-2.5 h-2.5 bg-primary-600 rounded-full"
                        />
                      </div>
                      <span class="text-sm text-gray-800 dark:text-gray-100">
                        {{ bp.phone }}
                        <span
                          v-if="bp.is_default"
                          class="ml-1 text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500"
                        >
                          основной
                        </span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- New phone input -->
                <div class="space-y-1">
                  <label class="text-xs font-semibold text-gray-600 dark:text-gray-300">
                    Ввести новый номер
                  </label>
                  <input
                    v-model="remotePaymentPhoneInput"
                    type="tel"
                    placeholder="+7 (___) ___-__-__"
                    class="w-full p-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
                    @input="onRemotePhoneInput"
                  />
                </div>

                <label class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-300">
                  <input
                    v-model="saveBillingPhone"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span>Сохранить этот номер для следующих заказов</span>
                </label>
              </div>
            </div>
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
import api from '@/services/api'

const router = useRouter()
const cartStore = useCartStore()
const ordersStore = useOrdersStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const loading = ref(false)
const dataLoaded = ref(false)

const billingPhones = ref([])
const selectedBillingPhoneId = ref(null)
const remotePaymentPhoneInput = ref('')
const saveBillingPhone = ref(true)
const showPhoneSelector = ref(false)

const form = reactive({
    phone: '',
    deliveryType: 'delivery',
    delivery_address_id: null,
    comment: '',
    payment_type_id: null,
    terminal_id: null
})

const selectedPayment = computed(() => {
    return ordersStore.paymentTypes.find(
        (pt) => pt.payment_id === form.payment_type_id
    )
})

const selectedPaymentSystemType = computed(() => {
    return selectedPayment.value?.system_type || null
})

const remotePaymentPhoneDisplay = computed(() => {
    if (remotePaymentPhoneInput.value.trim()) {
        return remotePaymentPhoneInput.value.trim()
    }
    const selected = billingPhones.value.find(
        (bp) => bp.id === selectedBillingPhoneId.value
    )
    return selected?.phone || authStore.user?.phone || ''
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

        // Load saved billing phones
        try {
            const response = await api.get('/phones/')
            billingPhones.value = response.data.results || response.data || []
            const defaultPhone =
              billingPhones.value.find((bp) => bp.is_default) ||
              billingPhones.value[0]
            if (defaultPhone) {
              selectedBillingPhoneId.value = defaultPhone.id
            }
        } catch (e) {
            console.error('Failed to load billing phones', e)
        }

        // Set default terminal if only one
        if (authStore.user.terminals?.length === 1) {
            form.terminal_id = authStore.user.terminals[0].terminal_id
        }
        
        // Если терминал не выбран, но есть терминалы - используем первый для загрузки продуктов
        if (!form.terminal_id && authStore.user.terminals?.length > 0) {
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

// Функция проверки рабочего времени
const checkWorkingHours = () => {
    // Определяем терминал
    let terminal = null
    if (form.terminal_id) {
        // Ищем терминал по terminal_id или id (оба могут быть в данных)
        terminal = authStore.user?.terminals?.find(t => 
            t.terminal_id === form.terminal_id || t.id === form.terminal_id
        )
    } else if (authStore.user?.terminals?.length === 1) {
        terminal = authStore.user.terminals[0]
    }
    
    // Если терминал не найден или нет настроек рабочего времени, пропускаем проверку
    if (!terminal || !terminal.working_hours || !terminal.working_hours.start || !terminal.working_hours.end) {
        return true // Разрешаем оформление, если рабочее время не настроено
    }
    
    const { start, end } = terminal.working_hours
    const now = new Date()
    const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    
    // Преобразуем время в минуты для удобства сравнения
    const timeToMinutes = (timeStr) => {
        const [hours, minutes] = timeStr.split(':').map(Number)
        return hours * 60 + minutes
    }
    
    const currentMinutes = timeToMinutes(currentTime)
    const startMinutes = timeToMinutes(start)
    const endMinutes = timeToMinutes(end)
    
    // Проверяем, находится ли текущее время в рабочем диапазоне
    let isWorkingTime = false
    
    if (startMinutes <= endMinutes) {
        // Обычный случай: рабочее время в пределах одного дня (например, 09:00 - 22:00)
        isWorkingTime = currentMinutes >= startMinutes && currentMinutes < endMinutes
    } else {
        // Переход через полночь (например, 18:00 - 04:00)
        // Рабочее время: с 18:00 до 23:59 или с 00:00 до 04:00
        isWorkingTime = currentMinutes >= startMinutes || currentMinutes < endMinutes
    }
    
    if (!isWorkingTime) {
        const message = `Извините, мы сейчас не принимаем заказы. Время работы: с ${start} до ${end}`
        telegramService.showAlert(message)
        return false
    }
    
    return true
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
    
    // Проверка рабочего времени
    if (!checkWorkingHours()) {
        return
    }

    loading.value = true
    try {
        // Normalize phone (remove spaces, parentheses, dashes etc.)
        const normalizedPhone = String(form.phone).replace(/[^\d+]/g, '')

        let remotePhone = remotePaymentPhoneDisplay.value
        remotePhone = String(remotePhone || '').replace(/[^\d+]/g, '')

        const orderData = {
            items: cartStore.getOrderData(),
            phone: normalizedPhone,
            comment: form.comment,
            payment_type_id: form.payment_type_id,
            terminal_id: form.terminal_id,
            delivery_address_id: form.deliveryType === 'delivery' ? form.delivery_address_id : null,
            remote_payment_phone: selectedPaymentSystemType.value === 'remote_payment' ? remotePhone : null,
            save_billing_phone: selectedPaymentSystemType.value === 'remote_payment' ? saveBillingPhone.value : false
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

const selectBillingPhone = (bp) => {
    selectedBillingPhoneId.value = bp.id
    remotePaymentPhoneInput.value = bp.phone
}

const onRemotePhoneInput = () => {
    // Явно сбрасываем выбранный сохранённый номер, если пользователь вводит новый
    if (remotePaymentPhoneInput.value.trim()) {
        selectedBillingPhoneId.value = null
    }
}
</script>
