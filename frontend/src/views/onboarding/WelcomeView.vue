<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 to-indigo-600 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 text-center">
      <!-- Icon -->
      <div class="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      </div>

      <!-- Title -->
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        Привет! 👋
      </h1>
      
      <!-- Description -->
      <div class="text-gray-600 mb-8 text-lg space-y-3">
        <p>
          Рады видеть тебя в <span class="font-semibold text-primary-600">{{ organizationName || 'нашем сервисе' }}</span>. Здесь можно быстро заказать любимые блюда.
        </p>
        <p>
          Для начала давай познакомимся — поделись своим номером телефона, чтобы мы могли сохранить твои будущие заказы и адреса доставки. Приятного аппетита! 🍕
        </p>
      </div>

      <!-- Button -->
      <button 
        @click="handleContinue"
        class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2 text-lg"
      >
        <span>Продолжить</span>
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organization'

const router = useRouter()
const authStore = useAuthStore()
const organizationStore = useOrganizationStore()

const organizationName = computed(() => {
  return authStore.user?.organization_name || organizationStore.organization?.org_name || null
})

onMounted(async () => {
  // Пытаемся загрузить организацию, если её ещё нет
  if (!organizationName.value && authStore.isAuthenticated) {
    try {
      await organizationStore.fetchOrganization()
    } catch (e) {
      // Игнорируем ошибки - название не критично
      console.log('Could not fetch organization:', e)
    }
  }
})

function handleContinue() {
  router.push('/onboarding/phone')
}
</script>
