import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import organizationService from '@/services/organization.service'

export const useOrganizationStore = defineStore('organization', () => {
    // State
    const organization = ref(null)
    const terminals = ref([])
    const paymentTypes = ref([])
    const externalMenus = ref([])
    const menuGroups = ref([]) // New state
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const hasOrganization = computed(() => !!organization.value)
    const hasIikoCredentials = computed(() => {
        return organization.value?.iiko_organization_id && organization.value?.api_key
    })

    // Actions

    /**
     * Fetch organization settings
     */
    async function fetchOrganization() {
        loading.value = true
        error.value = null

        try {
            const data = await organizationService.getOrganization()
            organization.value = data
            return data
        } catch (err) {
            console.error('Fetch organization error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить данные организации'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Update organization settings
     */
    async function updateOrganization(data) {
        loading.value = true
        error.value = null

        try {
            const updated = await organizationService.updateOrganization(data)
            organization.value = updated
            return updated
        } catch (err) {
            console.error('Update organization error:', err)
            const apiErr = err.response?.data
            if (typeof apiErr === 'string') {
                error.value = apiErr
            } else if (apiErr?.detail) {
                error.value = apiErr.detail
            } else if (apiErr?.error) {
                error.value = apiErr.error
            } else if (apiErr && typeof apiErr === 'object') {
                // Показываем field-errors (например unique/validation)
                error.value = Object.entries(apiErr)
                    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : String(v)}`)
                    .join('\n')
            } else {
                error.value = 'Не удалось обновить организацию'
            }
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Fetch terminals
     */
    async function fetchTerminals() {
        loading.value = true
        error.value = null

        try {
            const data = await organizationService.getTerminals()
            terminals.value = data
            return data
        } catch (err) {
            console.error('Fetch terminals error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить терминалы'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Load terminals from iiko
     */
    async function loadTerminalsFromIiko() {
        loading.value = true
        error.value = null

        try {
            const result = await organizationService.loadTerminalsFromIiko()
            await fetchTerminals() // Reload terminals list
            return result
        } catch (err) {
            console.error('Load terminals from iiko error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить терминалы из iiko'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Fetch payment types
     */
    async function fetchPaymentTypes() {
        loading.value = true
        error.value = null

        try {
            const data = await organizationService.getPaymentTypes()
            paymentTypes.value = data
            return data
        } catch (err) {
            console.error('Fetch payment types error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить типы оплат'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Load payment types from iiko
     */
    async function loadPaymentTypesFromIiko() {
        loading.value = true
        error.value = null

        try {
            const result = await organizationService.loadPaymentTypesFromIiko()
            await fetchPaymentTypes() // Reload payment types list
            return result
        } catch (err) {
            console.error('Load payment types from iiko error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить типы оплат из iiko'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Fetch external menus from iiko
     */
    async function fetchExternalMenus() {
        loading.value = true
        error.value = null

        try {
            const data = await organizationService.getExternalMenus()
            externalMenus.value = data
            return data
        } catch (err) {
            console.error('Fetch external menus error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить список меню'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Load menu from iiko (old method)
     */
    async function loadMenuFromIiko(menuId) {
        loading.value = true
        error.value = null

        try {
            const result = await organizationService.loadMenuFromIiko(menuId)
            return result
        } catch (err) {
            console.error('Load menu from iiko error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить меню из iiko'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Fetch Menu Groups (New)
     */
    async function fetchMenuGroups() {
        loading.value = true
        error.value = null
        try {
            const data = await organizationService.getMenuGroups()
            menuGroups.value = data
            return data
        } catch (err) {
            console.error('Fetch menu groups error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить группы меню'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Load Selected Menu Groups (New)
     */
    async function loadMenuGroups(selectedGroups) {
        loading.value = true
        error.value = null
        try {
            const result = await organizationService.loadMenuGroups(selectedGroups)
            return result
        } catch (err) {
            console.error('Load menu groups error:', err)
            error.value = err.response?.data?.detail || 'Не удалось загрузить выбранные группы'
            throw err
        } finally {
            loading.value = false
        }
    }

    /**
     * Clear error
     */
    function clearError() {
        error.value = null
    }

    return {
        // State
        organization,
        terminals,
        paymentTypes,
        externalMenus,
        menuGroups,
        loading,
        error,

        // Getters
        hasOrganization,
        hasIikoCredentials,

        // Actions
        fetchOrganization,
        updateOrganization,
        fetchTerminals,
        loadTerminalsFromIiko,
        fetchPaymentTypes,
        loadPaymentTypesFromIiko,
        fetchExternalMenus,
        loadMenuFromIiko,
        fetchMenuGroups,
        loadMenuGroups,
        clearError
    }
})
