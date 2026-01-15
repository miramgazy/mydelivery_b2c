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
}

export default new UserService()
