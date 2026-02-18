<template>
  <div class="min-h-screen flex flex-col" :style="rootStyles">
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
    </div>
    <template v-else>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWebsiteStore } from '@/stores/website'

const route = useRoute()
const router = useRouter()
const websiteStore = useWebsiteStore()
const loading = ref(true)

const orgId = computed(() => route.query.org || import.meta.env.VITE_ORG_ID || '')

const rootStyles = computed(() => {
  const s = websiteStore.styles
  if (!s) return {}
  return {
    '--primary-color': s.primary_color,
    '--secondary-color': s.secondary_color,
    '--background-color': s.background_color,
    '--font-main': s.font_family,
    '--radius-main': `${s.border_radius}px`,
  }
})

onMounted(async () => {
  await router.isReady()
  const id = orgId.value
  if (id) {
    try {
      await Promise.all([
        websiteStore.fetchStyles(id),
        websiteStore.fetchMenu(id),
      ])
    } catch (e) {
      console.error('Failed to load website data:', e)
    }
  }
  loading.value = false
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
