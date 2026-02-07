import api from './api'

class FastMenuService {
    async getGroups() {
        const response = await api.get('/fast-menu-groups/')
        const raw = response.data?.results ?? response.data
        return Array.isArray(raw) ? raw : []
    }

    async getGroup(id) {
        const response = await api.get(`/fast-menu-groups/${id}/`)
        return response.data
    }

    async createGroup(groupData) {
        const response = await api.post('/fast-menu-groups/', groupData)
        return response.data
    }

    async updateGroup(id, groupData) {
        const response = await api.patch(`/fast-menu-groups/${id}/`, groupData)
        return response.data
    }

    async deleteGroup(id) {
        await api.delete(`/fast-menu-groups/${id}/`)
    }

    async updateGroupItems(id, productIds) {
        const response = await api.put(`/fast-menu-groups/${id}/items/`, {
            product_ids: productIds
        })
        return response.data
    }

    // Публичный API для TMA
    async getPublicGroups(terminalId = null) {
        const params = terminalId ? { terminal_id: terminalId } : {}
        const response = await api.get('/fast-menu/', { params })
        return response.data?.results ?? response.data
    }
}

export default new FastMenuService()
