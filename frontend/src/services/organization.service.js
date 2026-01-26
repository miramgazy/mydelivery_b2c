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

// Update organization settings
export const updateOrganization = async (data) => {
    const response = await api.patch('/organizations/me/', data)
    return response.data
}

// Get terminals list
export const getTerminals = async () => {
    const response = await api.get('/organizations/terminals/')
    return response.data
}

// Load terminals from iiko
export const loadTerminalsFromIiko = async () => {
    const response = await api.post('/organizations/load-terminals/')
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

export const loadMenuFromIiko = async (menuId) => {
    // If no menuId, it just loads all/default
    const response = await api.post('/organizations/load-menu/', { external_menu_id: menuId })
    return response.data
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

export default {
    getOrganization,
    updateOrganization,
    getTerminals,
    loadTerminalsFromIiko,
    getPaymentTypes,
    loadPaymentTypesFromIiko,
    getExternalMenus,
    loadMenuFromIiko,
    getMenuGroups,
    loadMenuGroups,
    getAllOrganizations,
    updateTerminal,
    syncTerminalStopList
}
