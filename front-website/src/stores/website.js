import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useWebsiteStore = defineStore('website', () => {
  const styles = ref(null)
  const organization = ref(null)
  const categories = ref([])
  const products = ref([])
  const terminals = ref([])
  const loading = ref(false)
  const error = ref(null)

  const availableProducts = computed(() => {
    let result = products.value
    const selected = selectedCategory.value
    if (selected !== null && selected !== undefined) {
      result = result.filter(p => p.category?.subgroup_id === selected)
    }
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(p =>
        p.product_name?.toLowerCase().includes(q) ||
        p.description?.toLowerCase().includes(q)
      )
    }
    return result
  })

  const selectedCategory = ref(null)
  const searchQuery = ref('')

  async function fetchStyles(orgId) {
    try {
      const { data } = await api.get('/website/styles/', { params: { org: orgId } })
      styles.value = data
      return data
    } catch (err) {
      console.error('Fetch styles error:', err)
      styles.value = {
        primary_color: '#FF5733',
        secondary_color: '#333333',
        background_color: '#FFFFFF',
        font_family: 'Inter, sans-serif',
        border_radius: 12,
      }
      return styles.value
    }
  }

  async function fetchMenu(orgId, terminalId = null) {
    loading.value = true
    error.value = null
    try {
      const params = { org: orgId }
      if (terminalId) params.terminal_id = terminalId
      const { data } = await api.get('/website/menu/', { params })
      organization.value = data.organization
      categories.value = data.categories || []
      products.value = data.products || []
      terminals.value = data.terminals || []
      return data
    } catch (err) {
      console.error('Fetch menu error:', err)
      error.value = 'Не удалось загрузить меню'
      throw err
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

  return {
    styles,
    organization,
    categories,
    products,
    terminals,
    loading,
    error,
    availableProducts,
    selectedCategory,
    searchQuery,
    fetchStyles,
    fetchMenu,
    setSelectedCategory,
    setSearchQuery,
  }
})
