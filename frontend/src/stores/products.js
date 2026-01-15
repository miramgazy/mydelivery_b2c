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
    async function fetchCategories() {
        try {
            const response = await api.get('/categories/')
            categories.value = response.data.results || response.data
            return categories.value
        } catch (err) {
            console.error('Fetch categories error:', err)
            throw err
        }
    }

    async function fetchProducts() {
        try {
            const response = await api.get('/products/')
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

    async function refresh() {
        loading.value = true
        error.value = null
        try {
            await Promise.all([fetchCategories(), fetchProducts()])
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
