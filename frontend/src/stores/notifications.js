import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
    const message = ref('')
    const isVisible = ref(false)
    const timer = ref(null)

    function show(msg, duration = 2000) {
        // Clear existing timer
        if (timer.value) {
            clearTimeout(timer.value)
        }

        message.value = msg
        isVisible.value = true

        timer.value = setTimeout(() => {
            isVisible.value = false
            message.value = ''
            timer.value = null
        }, duration)
    }

    function hide() {
        isVisible.value = false
        if (timer.value) {
            clearTimeout(timer.value)
        }
        timer.value = null
    }

    return {
        message,
        isVisible,
        show,
        hide
    }
})
