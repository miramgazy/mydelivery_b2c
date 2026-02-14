import api from './api'

/**
 * Discount Service
 * Handles discount-related API calls (iiko sync)
 */

export const getDiscounts = async () => {
    const response = await api.get('/discounts/')
    const data = response.data
    // DRF без пагинации возвращает массив напрямую; с пагинацией — { results: [...] }
    const list = Array.isArray(data) ? data : (data?.results ?? data?.data ?? [])
    return Array.isArray(list) ? list : []
}

export const syncDiscounts = async () => {
    const response = await api.post('/discounts/sync/')
    return response.data
}

export const clearInactiveDiscounts = async () => {
    const response = await api.delete('/discounts/clear-inactive/')
    return response.data
}

export default {
    getDiscounts,
    syncDiscounts,
    clearInactiveDiscounts
}
