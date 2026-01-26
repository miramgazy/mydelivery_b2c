import api from './api'

class DeliveryAddressService {
    async getAddresses() {
        const response = await api.get('/addresses/')
        // DRF может вернуть либо массив, либо пагинацию { results: [...] }
        return response.data?.results ?? response.data
    }

    async getAddress(id) {
        const response = await api.get(`/addresses/${id}/`)
        return response.data
    }

    async createAddress(addressData) {
        const response = await api.post('/addresses/', addressData)
        return response.data
    }

    async updateAddress(id, addressData) {
        const response = await api.patch(`/addresses/${id}/`, addressData)
        return response.data
    }

    async deleteAddress(id) {
        await api.delete(`/addresses/${id}/`)
    }

    async setDefault(id) {
        const response = await api.post(`/addresses/${id}/set_default/`)
        return response.data
    }
}

export default new DeliveryAddressService()
