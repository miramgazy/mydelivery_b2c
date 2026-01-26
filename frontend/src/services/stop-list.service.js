import api from './api'

/**
 * Stop List Service
 * Handles all stop list related API calls
 */

// Get stop list
export const getStopList = async (params = {}) => {
    const response = await api.get('/stop-list/', { params })
    return response.data
}

// Create stop list entry
export const createStopListEntry = async (data) => {
    const response = await api.post('/stop-list/', data)
    return response.data
}

// Delete stop list entry
export const deleteStopListEntry = async (id) => {
    const response = await api.delete(`/stop-list/${id}/`)
    return response.data
}

export default {
    getStopList,
    createStopListEntry,
    deleteStopListEntry
}
