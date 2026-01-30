<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 to-indigo-600 flex items-center justify-center p-4">
    <!-- Language selection modal (first visit) -->
    <div
      v-if="showLanguageModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    >
      <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-6 text-center">
        <p class="text-gray-700 font-semibold mb-4">{{ t('language.selectLanguage') }}</p>
        <div class="flex flex-col gap-3">
          <button
            @click="selectLanguage('kz')"
            class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors active:scale-95"
          >
            {{ t('language.kz') }}
          </button>
          <button
            @click="selectLanguage('ru')"
            class="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-3 px-4 rounded-xl transition-colors active:scale-95"
          >
            {{ t('language.ru') }}
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 text-center">
      <!-- Icon -->
      <div class="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-12 h-12 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      </div>

      <!-- Title -->
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        {{ t('welcome.title') }}
      </h1>
      
      <!-- Description -->
      <div class="text-gray-600 mb-8 text-lg space-y-3">
        <p>
          {{ t('welcome.introPrefix') }}
          <span class="font-semibold text-primary-600">{{ organizationName || t('common.ourService') }}</span>
          {{ t('welcome.introSuffix') }}
        </p>
        <p>
          {{ t('welcome.introSecond') }}
        </p>
      </div>

      <!-- Button -->
      <button 
        @click="handleContinue"
        class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-4 px-6 rounded-xl transition-colors active:scale-95 flex items-center justify-center gap-2 text-lg"
      >
        <span>{{ t('common.continue') }}</span>
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useOrganizationStore } from '@/stores/organization'
import { getStoredLocale, setStoredLocale } from '@/i18n'
import authService from '@/services/auth.service'

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const organizationStore = useOrganizationStore()

const showLanguageModal = ref(false)

const organizationName = computed(() => {
  return authStore.user?.organization_name || organizationStore.organization?.org_name || null
})

onMounted(async () => {
  const stored = getStoredLocale()
  if (!stored) {
    showLanguageModal.value = true
    return
  }
  locale.value = stored
  if (!organizationName.value && authStore.isAuthenticated) {
    try {
      await organizationStore.fetchOrganization()
    } catch (e) {
      console.log('Could not fetch organization:', e)
    }
  }
})

watch(locale, (newLocale) => {
  setStoredLocale(newLocale)
  if (authStore.isAuthenticated && authService.isAuthenticated()) {
    authStore.updateProfile({ language_code: newLocale }).catch(() => {})
  }
})

function selectLanguage(code) {
  locale.value = code
  setStoredLocale(code)
  showLanguageModal.value = false
  if (authStore.isAuthenticated && authService.isAuthenticated()) {
    authStore.updateProfile({ language_code: code }).catch(() => {})
  }
}

function handleContinue() {
  if (showLanguageModal.value) return
  router.push('/onboarding/phone')
}
</script>
