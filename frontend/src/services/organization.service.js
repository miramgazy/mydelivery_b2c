import api from './api'

/**
 * Organization Service
 * Handles all organization-related API calls
 */

// Get organization settings
export const getOrganization = async () => {
    const response = await api.get('/organizations/me/')
    return response.data
}

// Update organization settings (PUT обходится с прокси/брандмауэрами, где PATCH даёт 405)
export const updateOrganization = async (data) => {
    const response = await api.put('/organizations/me/', data)
    return response.data
}

// Отправить тестовый JSON на webhook_link организации
export const testWebhook = async () => {
    const response = await api.post('/organizations/test-webhook/')
    return response.data
}

// Установить вебхук в Telegram для получения телефона
export const setWebhook = async (orgId) => {
    // URL action detail=True, поэтому путь /organizations/<orgId>/set-webhook/
    const response = await api.post(`/organizations/${orgId}/set-webhook/`)
    return response.data
}

// Получить информацию о вебхуке из Telegram
export const getWebhookInfo = async (orgId) => {
    const response = await api.get(`/organizations/${orgId}/webhook-info/`)
    return response.data
}

// Get terminals list
export const getTerminals = async () => {
    const response = await api.get('/organizations/terminals/')
    return response.data
}

// Load terminals from iiko (supports optional rmsBaseId)
export const loadTerminalsFromIiko = async (rmsBaseId = null) => {
    const payload = rmsBaseId ? { rms_base_id: rmsBaseId } : {}
    const response = await api.post('/organizations/load-terminals/', payload)
    return response.data
}

// Get RMS bases list
export const getRmsBases = async (params = {}) => {
    const response = await api.get('/rms-bases/', { params })
    return response.data.results || response.data
}

// Create RMS base
export const createRmsBase = async (data) => {
    const response = await api.post('/rms-bases/', data)
    return response.data
}

// Update RMS base
export const updateRmsBase = async (id, data) => {
    const response = await api.patch(`/rms-bases/${id}/`, data)
    return response.data
}

// Delete RMS base
export const deleteRmsBase = async (id) => {
    const response = await api.delete(`/rms-bases/${id}/`)
    return response.data
}

// Sync terminals for a single RMS base
export const syncRmsTerminals = async (rmsId) => {
    const response = await api.post(`/rms-bases/${rmsId}/sync-terminals/`)
    return response.data
}

// Get payment types
export const getPaymentTypes = async () => {
    const response = await api.get('/organizations/payment-types/')
    return response.data
}

// Load payment types from iiko
export const loadPaymentTypesFromIiko = async () => {
    const response = await api.post('/organizations/load-payment-types/')
    return response.data
}

// Get available external menus from iiko
export const getExternalMenus = async () => {
    const response = await api.get('/organizations/external-menus/')
    return response.data
}

// Get available menu groups (root groups)
export const getMenuGroups = async () => {
    const response = await api.get('/organizations/menu-groups/')
    return response.data
}

// Load selected menu groups
export const loadMenuGroups = async (selectedGroups) => {
    const response = await api.post('/organizations/load-menu-groups/', { selected_groups: selectedGroups })
    return response.data
}

export const loadMenuFromIiko = async (payload) => {
    // payload: { external_menu_id?, price_category_id?, menu_name?, price_category_name? }
    const response = await api.post('/organizations/load-menu/', payload)
    return response.data
}

// Get menus list (for_management=1 returns all menus for org)
export const getMenus = async (forManagement = false) => {
    const params = forManagement ? { for_management: '1' } : {}
    const response = await api.get('/menus/', { params })
    return response.data.results ?? response.data
}

// Update menu (e.g. is_active). menuId — UUID меню (menu_id).
export const updateMenu = async (menuId, data) => {
    const id = menuId != null ? String(menuId) : ''
    const response = await api.patch(`/menus/${id}/`, data)
    return response.data
}

// Delete menu (cascade: categories, products, modifiers). Fails if there are orders with items from this menu.
export const deleteMenu = async (menuId) => {
    const id = menuId != null ? String(menuId) : ''
    await api.delete(`/menus/${id}/`)
}

// Get all active organizations
export const getAllOrganizations = async () => {
    const response = await api.get('/organizations/', {
        params: { is_active: true }
    })
    return response.data.results || response.data
}

// Update terminal
export const updateTerminal = async (terminalId, data) => {
    const response = await api.patch(`/terminals/${terminalId}/`, data)
    return response.data
}

// Sync stop list for terminal
export const syncTerminalStopList = async (terminalId) => {
    const response = await api.post(`/terminals/${terminalId}/sync-stop-list/`)
    return response.data
}

// Update delivery zones for terminal
export const updateTerminalDeliveryZones = async (terminalId, deliveryZones) => {
    const response = await api.patch(`/terminals/${terminalId}/delivery-zones/`, {
        delivery_zones_conditions: deliveryZones
    })
    return response.data
}

// Toggle terminal active status
export const toggleTerminalActive = async (terminalId) => {
    const response = await api.patch(`/terminals/${terminalId}/toggle-active/`)
    return response.data
}

// Calculate delivery cost for coordinates
export const calculateDeliveryCost = async (terminalId, latitude, longitude, orderAmount = 0) => {
    const response = await api.post(`/terminals/${terminalId}/calculate-delivery-cost/`, {
        latitude,
        longitude,
        order_amount: orderAmount
    })
    return response.data
}

// Get cities list
export const getCities = async (organizationId = null) => {
    const params = {}
    if (organizationId) {
        params.organization = organizationId
    }
    const response = await api.get('/cities/', { params })
    return response.data.results || response.data
}

export default {
    getOrganization,
    updateOrganization,
    testWebhook,
    setWebhook,
    getWebhookInfo,
    getTerminals,
    loadTerminalsFromIiko,
    getRmsBases,
    createRmsBase,
    updateRmsBase,
    deleteRmsBase,
    syncRmsTerminals,
    getPaymentTypes,
    loadPaymentTypesFromIiko,
    getExternalMenus,
    loadMenuFromIiko,
    getMenus,
    updateMenu,
    deleteMenu,
    getMenuGroups,
    loadMenuGroups,
    getAllOrganizations,
    updateTerminal,
    syncTerminalStopList,
    updateTerminalDeliveryZones,
    toggleTerminalActive,
    getCities,
    calculateDeliveryCost
}
