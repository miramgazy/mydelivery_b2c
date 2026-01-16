import api, { setAuthToken, setRefreshToken } from './api'
import telegramService from './telegram'

class AuthService {
    /**
     * Проверка доступа пользователя по Telegram ID
     */
    async checkAccess(telegramId) {
        try {
            console.log('API Request: check_access for', telegramId)
            const response = await api.post('/users/check_access/', {
                telegram_id: telegramId
            }, {
                skipAuth: true
            })
            console.log('API Response: check_access success')
            return response.data
        } catch (error) {
            console.error('API Error: check_access', error.message)
            throw error
        }
    }

    /**
     * Аутентификация через Telegram Mini App
     */
    /**
     * Аутентификация через Telegram Mini App
     */
    async loginWithTelegram() {
        try {
            const initData = telegramService.getInitData()
            if (!initData) throw new Error('Telegram initData not available')

            const response = await api.post('/auth/telegram/', {
                initData: initData
            }, {
                skipAuth: true
            })

            const { access, refresh, user } = response.data
            setAuthToken(access)
            setRefreshToken(refresh)

            return {
                success: true,
                user,
                message: response.data.message
            }
        } catch (error) {
            const msg = error.response?.data?.message || error.message
            console.error('Login error:', msg)
            return {
                success: false,
                message: msg
            }
        }
    }

    /**
     * Аутентификация по логину и паролю
     */
    async loginWithPassword(username, password) {
        try {
            const response = await api.post('/token/', {
                username,
                password
            }, {
                skipAuth: true
            });

            const { access, refresh } = response.data;
            setAuthToken(access);
            setRefreshToken(refresh);

            // После получения токена загружаем пользователя
            const user = await this.getCurrentUser();

            return {
                success: true,
                user
            };
        } catch (error) {
            console.error('Login with password failed:', error);
            throw error;
        }
    }

    /**
     * Получить текущего пользователя
     */
    async getCurrentUser() {
        try {
            const response = await api.get('/users/me/');
            return response.data;
        } catch (error) {
            console.error('Get current user failed:', error);
            throw error;
        }
    }

    /**
     * Обновить профиль
     */
    async updateProfile(data) {
        try {
            const response = await api.patch('/users/me/', data);
            return response.data;
        } catch (error) {
            console.error('Update profile failed:', error);
            throw error;
        }
    }

    /**
     * Проверка, авторизован ли пользователь (есть ли токен)
     */
    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    /**
     * Выход из системы
     */
    logout() {
        setAuthToken(null);
        setRefreshToken(null);
        // Опционально: api.post('/logout/') если нужно инвелидировать на бэке
        if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
            window.location.href = '/login';
        }
    }
}

export default new AuthService()