import api, { setAuthToken, setRefreshToken, clearTokens } from './api'
import telegramService from './telegram'

class AuthService {
    /**
     * Проверка доступа пользователя по Telegram ID
     * Вызывается ДО попытки аутентификации
     */
    async checkAccess(telegramId) {
        try {
            alert(`СЕРВИС: Отправляю POST на /api/users/check_access/ для ID ${telegramId}`)
            const response = await api.post('/users/check_access/', {
                telegram_id: telegramId
            }, {
                skipAuth: true
            })
            alert('СЕРВИС: Ответ получен!')
            return response.data
        } catch (error) {
            console.error('Check access error:', error)
            throw error
        }
    }

    /**
     * Аутентификация через Telegram Mini App
     */
    async loginWithTelegram() {
        try {
            const initData = telegramService.getInitData()

            if (!initData) {
                throw new Error('Telegram initData not available')
            }

            const response = await api.post('/auth/telegram/', {
                initData: initData
            })

            const { access, refresh, user } = response.data

            // Сохраняем токены
            setAuthToken(access)
            setRefreshToken(refresh)

            return {
                success: true,
                user,
                message: response.data.message
            }
        } catch (error) {
            console.error('Login error:', error)

            // Обрабатываем ошибки B2B
            if (error.response?.data) {
                const errorData = error.response.data
                return {
                    success: false,
                    error: errorData.error || 'Ошибка входа',
                    message: errorData.message,
                    code: errorData.code,
                    telegram_id: errorData.telegram_id
                }
            }

            throw error
        }
    }

    /**
     * Аутентификация через логин и пароль (для админов)
     */
    async loginWithPassword(username, password) {
        try {
            const response = await api.post('/token/', {
                username,
                password
            })

            const { access, refresh } = response.data

            // Сохраняем токены
            setAuthToken(access)
            setRefreshToken(refresh)

            // После получения токена запрашиваем данные пользователя
            const user = await this.getCurrentUser()

            return {
                success: true,
                user
            }
        } catch (error) {
            console.error('Password login error:', error)
            throw error
        }
    }

    /**
     * Выход из системы
     */
    logout() {
        clearTokens()
    }

    /**
     * Получить текущего пользователя
     */
    async getCurrentUser() {
        try {
            const response = await api.get('/users/me/')
            return response.data
        } catch (error) {
            console.error('Get current user error:', error)
            throw error
        }
    }

    /**
     * Обновление данных пользователя
     */
    async updateProfile(data) {
        try {
            const response = await api.put('/users/me/', data)
            return response.data
        } catch (error) {
            console.error('Update profile error:', error)
            throw error
        }
    }

    /**
     * Проверка авторизации
     */
    isAuthenticated() {
        return !!localStorage.getItem('access_token')
    }
}

export default new AuthService()