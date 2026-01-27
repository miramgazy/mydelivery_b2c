import axios from 'axios'

// Принудительно используем относительный путь для продакшена в TMA
const API_URL = '/api'

// Создаем экземпляр axios
const api = axios.create({
    baseURL: API_URL,
    timeout: 10000, // 10 секунд жесткий таймаут
    headers: {
        'Content-Type': 'application/json',
    },
})

// Interceptor для добавления токена
api.interceptors.request.use(
    (config) => {
        console.log('AXIOS REQUEST: Sending to ' + config.url)
        const token = localStorage.getItem('access_token')

        if (token && !config.skipAuth) {
            config.headers.Authorization = `Bearer ${token}`
        }

        // Анти-кэш только для POST/PUT/DELETE или если явно указано skipCacheBust: false
        // Для GET запросов не добавляем _t, чтобы использовать кэш браузера/прокси
        const method = config.method?.toLowerCase() || 'get'
        const shouldBustCache = config.skipCacheBust === false || 
                               ['post', 'put', 'patch', 'delete'].includes(method)
        
        if (shouldBustCache) {
            config.params = config.params || {};
            config.params._t = Date.now();
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Interceptor для обработки ответов
api.interceptors.response.use(
    (response) => {
        console.log(`AXIOS RESPONSE: Received from ${response.config.url}. Status: ${response.status}`)
        return response
    },
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