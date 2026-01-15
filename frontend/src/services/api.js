import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Создаем экземпляр axios
const api = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Interceptor для добавления токена
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')

        if (config.skipAuth) {
            delete config.headers.Authorization
            return config
        }

        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Interceptor для обработки ответов
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // Если 401 и это не повторный запрос - пробуем обновить токен
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                if (!refreshToken) {
                    throw new Error('No refresh token')
                }

                const response = await axios.post(`${API_URL}/token/refresh/`, {
                    refresh: refreshToken,
                })

                const { access } = response.data
                localStorage.setItem('access_token', access)

                originalRequest.headers.Authorization = `Bearer ${access}`
                return api(originalRequest)
            } catch (refreshError) {
                // Не удалось обновить токен - выходим
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')

                // Перенаправляем на экран входа
                if (window.location.pathname !== '/') {
                    window.location.href = '/'
                }

                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

export default api

// Вспомогательные функции
export const setAuthToken = (token) => {
    if (token) {
        localStorage.setItem('access_token', token)
    } else {
        localStorage.removeItem('access_token')
    }
}

export const setRefreshToken = (token) => {
    if (token) {
        localStorage.setItem('refresh_token', token)
    } else {
        localStorage.removeItem('refresh_token')
    }
}

export const getAuthToken = () => {
    return localStorage.getItem('access_token')
}

export const clearTokens = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
}