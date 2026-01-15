<template>
  <Transition name="toast">
    <div
      v-if="store.isVisible"
      class="fixed top-8 left-1/2 -translate-x-1/2 z-[100] w-[calc(100%-2rem)] max-w-sm"
    >
      <div class="bg-gray-900/90 backdrop-blur-md text-white px-6 py-3 rounded-2xl shadow-xl border border-white/10 flex items-center gap-3">
        <div class="p-1.5 bg-primary-500 rounded-lg">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p class="text-sm font-medium">{{ store.message }}</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notifications'

const store = useNotificationStore()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -100%);
}
</style>
