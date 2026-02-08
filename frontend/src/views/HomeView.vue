<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header (цвет из настроек организации или голубой по умолчанию) -->
    <div
      class="pt-5 pb-5 px-4 rounded-b-3xl relative overflow-hidden"
      :style="{ backgroundColor: headerColor }"
    >
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12"></div>
        
        <div class="relative z-10">
            <div class="flex justify-between items-start mb-1">
                <p class="text-white text-lg font-semibold">
                    {{ t('home.greeting', { name: user?.first_name || t('common.guest') }) }}
                </p>
                <!-- Language switcher (KZ | RU) -->
                <div class="flex items-center gap-1 text-white/90 text-sm font-medium">
                    <button
                        type="button"
                        :class="locale === 'kz' ? 'text-white font-bold underline' : 'hover:text-white'"
                        @click="setLocale('kz')"
                    >
                        KZ
                    </button>
                    <span class="opacity-60">|</span>
                    <button
                        type="button"
                        :class="locale === 'ru' ? 'text-white font-bold underline' : 'hover:text-white'"
                        @click="setLocale('ru')"
                    >
                        RU
                    </button>
                </div>
            </div>
            <p class="text-white mb-3 text-sm leading-relaxed opacity-95">
                {{ t('home.subtitle', { company: companyName || '—', terminal: terminalName || '—' }) }}
            </p>
            
            <!-- Quick Actions -->
            <router-link 
                to="/menu"
                class="block w-full bg-white rounded-xl p-4 shadow-lg active:scale-95 transition-transform flex items-center justify-between group"
                :style="{ color: headerColor }"
            >
                <div class="flex items-center gap-4">
                    <div class="p-3 rounded-full opacity-90" :style="{ backgroundColor: headerColor + '20' }">
                        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                    </div>
                    <div class="text-left">
                        <p class="font-bold text-lg">{{ t('home.makeOrder') }}</p>
                        <p class="text-sm text-gray-500">{{ t('home.makeOrderHint') }}</p>
                    </div>
                </div>
                <svg class="w-6 h-6 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </router-link>

            <!-- Instagram + language row: Instagram on the right -->
            <div class="flex justify-end items-center gap-2 mt-2">
                <a
                    v-if="currentTerminalInstagramLink"
                    :href="currentTerminalInstagramLink"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
                    aria-label="Instagram"
                >
                    <svg class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                        <path fill-rule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.048-1.067-.06-1.407-.06-4.123v-.08c0-2.643.012-2.987.06-4.043.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.993 2.013 9.337 2 11.965 2h.08c.013 0 .028 0 .043.002h.014zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clip-rule="evenodd" />
                    </svg>
                </a>
            </div>
        </div>
    </div>

    <!-- Active Orders Preview -->
    <div class="px-4 -mt-5 relative z-10" v-if="activeOrder">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border-l-4 border-yellow-400">
            <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-gray-900 dark:text-white">{{ t('home.activeOrder') }}</h3>
                <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">{{ activeOrder.status_display }}</span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {{ t('orders.order') }} #{{ activeOrder.order_number }}
            </p>
            <router-link 
                :to="'/orders/' + activeOrder.order_id"
                class="text-sm font-semibold hover:underline"
                :style="{ color: headerColor }"
            >
                {{ t('home.trackStatus') }}
            </router-link>
        </div>
    </div>

    <!-- Fast Menu Groups (tiles with image, 2 columns) -->
    <div class="px-4 mt-4" v-if="fastMenuGroups.length > 0">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3">{{ t('home.fastMenu') }}</h3>
        <div class="grid grid-cols-2 gap-3 pb-2">
            <button
                v-for="group in fastMenuGroups"
                :key="group.id"
                @click="openFastMenuGroup(group)"
                class="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700 overflow-hidden text-left h-[9.5rem]"
            >
                <!-- Верхняя часть: картинка -->
                <div class="flex-1 min-h-0 w-full bg-gray-200 dark:bg-gray-700">
                    <img
                        v-if="group.image_url"
                        :src="normalizeMediaUrl(group.image_url)"
                        :alt="group.name"
                        class="w-full h-full object-cover"
                    />
                    <div
                        v-else
                        class="w-full h-full flex items-center justify-center text-gray-400 dark:text-gray-500"
                    >
                        <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14" />
                        </svg>
                    </div>
                </div>
                <!-- Нижняя часть: название -->
                <div class="flex-shrink-0 px-3 py-2 border-t border-gray-100 dark:border-gray-700">
                    <span class="font-semibold text-gray-900 dark:text-white text-sm line-clamp-2">{{ group.name }}</span>
                </div>
            </button>
        </div>
    </div>

    <!-- Features Grid (compact: My orders & Profile) -->
    <div class="p-4 grid grid-cols-2 gap-3 mt-2">
        <router-link to="/orders" class="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-sm hover:shadow-md transition-shadow flex items-center gap-3">
            <div class="w-9 h-9 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
            </div>
            <div class="min-w-0">
                <h3 class="font-bold text-gray-900 dark:text-white text-sm">{{ t('home.myOrders') }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ t('home.myOrdersHint') }}</p>
            </div>
        </router-link>

        <router-link to="/profile" class="bg-white dark:bg-gray-800 p-3 rounded-xl shadow-sm hover:shadow-md transition-shadow flex items-center gap-3">
            <div class="w-9 h-9 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
            </div>
            <div class="min-w-0">
                <h3 class="font-bold text-gray-900 dark:text-white text-sm">{{ t('home.profile') }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ t('home.profileHint') }}</p>
            </div>
        </router-link>
        
        <div v-if="isAdmin" class="col-span-2">
             <router-link to="/admin" class="flex items-center gap-4 bg-gray-900 dark:bg-gray-700 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow text-white">
                <div class="w-10 h-10 bg-gray-700 dark:bg-gray-600 rounded-full flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </div>
                <div>
                    <h3 class="font-bold">{{ t('home.adminPanel') }}</h3>
                    <p class="text-xs text-gray-400">{{ t('home.adminPanelHint') }}</p>
                </div>
             </router-link>
        </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useOrdersStore } from '@/stores/orders'
import { useOrganizationStore } from '@/stores/organization'
import fastMenuService from '@/services/fast-menu.service'
import { setStoredLocale } from '@/i18n'
import authService from '@/services/auth.service'
import { normalizeMediaUrl } from '@/utils/mediaUrl'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const ordersStore = useOrdersStore()
const organizationStore = useOrganizationStore()

const headerColor = computed(() => {
  const c = organizationStore.organization?.primary_color
  return (c && /^#[0-9A-Fa-f]{6}$/.test(c)) ? c : '#0284c7'
})

function setLocale(code) {
  locale.value = code
  setStoredLocale(code)
  if (authStore.isAuthenticated && authService.isAuthenticated()) {
    authStore.updateProfile({ language_code: code }).catch(() => {})
  }
}

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isSuperAdmin || authStore.isOrgAdmin)
const activeOrder = computed(() => ordersStore.activeOrders[0])
const fastMenuGroups = ref([])

const companyName = computed(() => user.value?.organization_name || null)
const currentTerminal = computed(() => user.value?.terminals?.[0] || null)
const terminalName = computed(() => currentTerminal.value?.name || currentTerminal.value?.terminal_group_name || null)
const currentTerminalInstagramLink = computed(() => currentTerminal.value?.instagram_link || null)

onMounted(async () => {
    // Цвет шапки из настроек организации
    organizationStore.fetchOrganization().catch(console.error)
    ordersStore.fetchMyOrders().catch(console.error)
    
    // Load fast menu groups
    try {
        const terminalId = user.value?.terminals?.[0]?.terminal_id || user.value?.terminals?.[0]?.id || null
        fastMenuGroups.value = await fastMenuService.getPublicGroups(terminalId)
    } catch (err) {
        console.error('Failed to load fast menu groups:', err)
    }
})

const openFastMenuGroup = (group) => {
    router.push({
        name: 'fast-menu-group',
        params: { groupId: group.id },
        query: { name: group.name }
    })
}
</script>

<style scoped>
.pb-safe-bottom {
    padding-bottom: calc(0.5rem + env(safe-area-inset-bottom));
}
</style>
