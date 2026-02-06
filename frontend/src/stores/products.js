import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useProductsStore = defineStore('products', () => {
    // State
    const categories = ref([])
    const products = ref([])
    const selectedCategory = ref(null)
    const searchQuery = ref('')
    const loading = ref(false)
    const error = ref(null)

    // Getters
    const availableProducts = computed(() => {
        let result = products.value

        // Фильтр по категории
        if (selectedCategory.value !== null && selectedCategory.value !== undefined) {
            result = result.filter(p => p.category?.subgroup_id === selectedCategory.value)
        }

        // Поиск
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase()
            result = result.filter(p =>
                p.product_name.toLowerCase().includes(query) ||
                (p.description && p.description.toLowerCase().includes(query))
            )
        }

        return result
    })

    // Actions
    async function fetchCategories(forManagement = false) {
        try {
            const params = forManagement ? { for_management: '1' } : {}
            const response = await api.get('/categories/', { params })
            categories.value = response.data.results || response.data
            return categories.value
        } catch (err) {
            console.error('Fetch categories error:', err)
            throw err
        }
    }

    async function fetchProducts(terminalId = null, forManagement = false) {
        try {
            const params = {}
            if (forManagement) params.for_management = '1'

            // Если terminal_id не передан, пытаемся определить из auth store
            if (!terminalId) {
                const { useAuthStore } = await import('@/stores/auth')
                const authStore = useAuthStore()
                const user = authStore.user

                if (user?.terminals && user.terminals.length > 0) {
                    // Используем первый терминал, если их несколько
                    terminalId = user.terminals[0].terminal_id || user.terminals[0].id
                }
            }

            if (terminalId) {
                params.terminal_id = terminalId
            }

            const response = await api.get('/products/', { params })
            products.value = response.data.results || response.data

            // Обогащаем данными о количестве в категории
            updateCategoriesCounts()

            return products.value
        } catch (err) {
            console.error('Fetch products error:', err)
            throw err
        }
    }

    function updateCategoriesCounts() {
        categories.value.forEach(cat => {
            const count = products.value.filter(p => p.category?.subgroup_id === cat.subgroup_id).length
            cat.products_count = count
        })
    }

    async function refresh(terminalId = null) {
        loading.value = true
        error.value = null
        try {
            await Promise.all([fetchCategories(), fetchProducts(terminalId)])
        } catch (err) {
            error.value = 'Не удалось загрузить меню'
        } finally {
            loading.value = false
        }
    }

    function setSelectedCategory(id) {
        selectedCategory.value = id
    }

    function setSearchQuery(query) {
        searchQuery.value = query
    }

    function clearFilters() {
        selectedCategory.value = null
        searchQuery.value = ''
    }

    return {
        // State
        categories,
        products,
        selectedCategory,
        searchQuery,
        loading,
        error,

        // Getters
        availableProducts,

        // Actions
        refresh,
        fetchCategories,
        fetchProducts,
        setSelectedCategory,
        setSearchQuery,
        clearFilters
    }
})
