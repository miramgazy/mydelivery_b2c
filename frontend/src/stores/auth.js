import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth.service'
import telegramService from '@/services/telegram'

export const useAuthStore = defineStore('auth', () => {
    // State
    const user = ref(null)
    const loading = ref(false)
    const accessCheckResult = ref(null)
    const error = ref(null)

    // Getters
    const isAuthenticated = computed(() => !!user.value)
    const isSuperAdmin = computed(() => user.value?.role_name === 'superadmin')
    const isOrgAdmin = computed(() => user.value?.role_name === 'org_admin')
    const isCustomer = computed(() => user.value?.role_name === 'customer')
    const hasAccess = computed(() => accessCheckResult.value?.has_access === true)

    // Actions

    /**
     * Проверка доступа пользователя
     * Первый шаг - проверяем зарегистрирован ли пользователь
     */
    async function checkAccess() {
        loading.value = true
        error.value = null

        try {
            const telegramUser = telegramService.getUser()
            if (!telegramUser?.id) throw new Error('Нет ID Telegram')

            console.log('Calling authService.checkAccess for id:', telegramUser.id);
            const result = await authService.checkAccess(telegramUser.id);
            console.log('CheckAccess result from service:', result);

            accessCheckResult.value = result
            return result
        } catch (err) {
            console.error('CheckAccess error in store:', err);
            accessCheckResult.value = { has_access: false, message: err.message }
            return accessCheckResult.value
        } finally {
            loading.value = false
        }
    }

    /**
     * Аутентификация через Telegram
     * Второй шаг - если доступ есть, аутентифицируемся
     */
    async function login() {
        loading.value = true
        error.value = null

        try {
            const result = await authService.loginWithTelegram()

            if (result.success) {
                user.value = result.user
                return {
                    success: true,
                    message: result.message || 'Вход выполнен успешно'
                }
            } else {
                error.value = result.message || result.error
                return {
                    success: false,
                    error: result.error,
                    message: result.message,
                    code: result.code,
                    telegram_id: result.telegram_id
                }
            }
        } catch (err) {
            console.error('Login error:', err)
            error.value = 'Ошибка при входе в систему'
            return {
                success: false,
                error: error.value
            }
        } finally {
            loading.value = false
        }
    }

    /**
     * Аутентификация через логин и пароль
     */
    async function loginWithPassword(username, password) {
        loading.value = true
        error.value = null

        try {
            const result = await authService.loginWithPassword(username, password)
            if (result.success) {
                // Всегда загружаем свежие данные пользователя с сервера
                await fetchCurrentUser()
                return { success: true }
            }
            return { success: false, error: 'Ошибка входа' }
        } catch (err) {
            console.error('Login with password error:', err)
            error.value = err.response?.data?.detail || 'Неверный логин или пароль'
            return {
                success: false,
                error: error.value
            }
        } finally {
            loading.value = false
        }
    }

    /**
     * Загрузка данных текущего пользователя
     */
    async function fetchCurrentUser() {
        if (!authService.isAuthenticated()) {
            return null
        }

        loading.value = true
        error.value = null

        try {
            const userData = await authService.getCurrentUser()
            user.value = userData
            return userData
        } catch (err) {
            console.error('Fetch current user error:', err)
            error.value = 'Не удалось загрузить данные пользователя'

            // Если 401 - токен невалиден, выходим
            if (err.response?.status === 401) {
                logout()
            }

            return null
        } finally {
            loading.value = false
        }
    }

    /**
     * Обновление профиля
     */
    async function updateProfile(data) {
        loading.value = true
        error.value = null

        try {
            const updated = await authService.updateProfile(data)
            user.value = { ...user.value, ...updated }
            return updated
        } catch (err) {
            console.error('Update profile error:', err)
            error.value = 'Не удалось обновить профиль'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Выход из системы
     */
    function logout() {
        authService.logout()
        user.value = null
        accessCheckResult.value = null
        error.value = null
    }

    /**
     * Очистка ошибки
     */
    function clearError() {
        error.value = null
    }

    return {
        // State
        user,
        loading,
        accessCheckResult,
        error,

        // Getters
        isAuthenticated,
        isSuperAdmin,
        isOrgAdmin,
        isCustomer,
        hasAccess,

        // Actions
        checkAccess,
        login,
        loginWithPassword,
        fetchCurrentUser,
        updateProfile,
        logout,
        clearError
    }
})