import api from './api'

class UserService {
    async getUsers() {
        const response = await api.get('/users/')
        return response.data
    }

    async createUser(userData) {
        const response = await api.post('/users/', userData)
        return response.data
    }

    async updateUser(id, userData) {
        const response = await api.patch(`/users/${id}/`, userData)
        return response.data
    }

    async deleteUser(id) {
        await api.delete(`/users/${id}/`)
    }

    async getRoles() {
        const response = await api.get('/roles/')
        return response.data
    }

    async updateProfile(userData) {
        const response = await api.patch('/users/me/', userData)
        return response.data
    }

    async getBotSyncToken() {
        const response = await api.post('/users/bot-sync-token/')
        return response.data
    }

    async checkBotSubscription() {
        const response = await api.get('/users/check-bot-subscription/')
        return response.data
    }

    async declineBotSubscription() {
        const response = await api.post('/users/decline-bot-subscription/')
        return response.data
    }
}

export default new UserService()
