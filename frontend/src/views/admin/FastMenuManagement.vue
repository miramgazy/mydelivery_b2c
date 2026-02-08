<template>
  <div class="max-w-7xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm">
      <!-- Header -->
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Быстрое меню</h2>
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Icon icon="mdi:plus" class="w-5 h-5" />
            Создать быстрое меню
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Empty State -->
      <div
        v-else-if="groups.length === 0"
        class="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400"
      >
        <Icon icon="mdi:flash-off" class="w-16 h-16 mb-4" />
        <p class="text-lg font-medium">Группы быстрого меню не созданы</p>
        <p class="text-sm">Создайте первую группу для быстрого доступа к товарам</p>
      </div>

      <!-- Groups Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Название
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Товаров
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Порядок
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="group in groups"
              :key="group.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <Icon icon="mdi:flash" class="w-5 h-5 text-yellow-500" />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ group.name }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-900 dark:text-white">
                  {{ group.items_count || 0 }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm text-gray-900 dark:text-white">
                  {{ group.order }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    group.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  {{ group.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    @click="openEditModal(group)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    <Icon icon="mdi:pencil" class="w-5 h-5" />
                  </button>
                  <button
                    @click="confirmDelete(group)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                  >
                    <Icon icon="mdi:delete" class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
      >
        <!-- Modal Header -->
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">
            {{ editingGroup ? 'Редактировать группу' : 'Создать группу быстрого меню' }}
          </h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <Icon icon="mdi:close" class="w-6 h-6" />
          </button>
        </div>

        <!-- Modal Body (скроллится) -->
        <div class="p-6 overflow-y-auto flex-1 min-h-0">
          <form id="fast-menu-group-form" @submit.prevent="saveGroup" class="space-y-6">
            <!-- Group Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Название группы
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                placeholder="Например: Популярное, Завтраки"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- Order -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Порядок сортировки
              </label>
              <input
                v-model.number="form.order"
                type="number"
                min="0"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- Is Active -->
            <div class="flex items-center gap-2">
              <input
                v-model="form.is_active"
                type="checkbox"
                id="is_active"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label for="is_active" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Группа активна
              </label>
            </div>

            <!-- Image for tile -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Изображение для плитки (отображается в быстром меню в приложении)
              </label>
              <div class="flex flex-col sm:flex-row gap-4 items-start">
                <div class="w-32 h-24 rounded-lg bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0 border border-gray-300 dark:border-gray-600">
                  <img
                    v-if="imagePreviewUrl"
                    :src="displayImageUrl"
                    alt="Превью"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                    <Icon icon="mdi:image-plus" class="w-10 h-10" />
                  </div>
                </div>
                <div class="flex flex-col gap-1">
                  <input
                    ref="imageFileRef"
                    type="file"
                    accept="image/*"
                    class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900/30 dark:file:text-blue-300"
                    @change="onImageChange"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    Рекомендуется изображение в пропорции примерно 1:1 или горизонтальное
                  </p>
                </div>
              </div>
            </div>

            <!-- Products Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Выбор товаров
              </label>
              
              <!-- Search -->
              <input
                v-model="productSearch"
                type="text"
                placeholder="Поиск по названию товара..."
                class="w-full mb-4 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />

              <!-- Products List -->
              <div class="border border-gray-300 dark:border-gray-600 rounded-lg max-h-96 overflow-y-auto">
                <div v-if="loadingProducts" class="p-4 text-center">
                  <Icon icon="mdi:loading" class="w-6 h-6 animate-spin text-blue-600 mx-auto" />
                </div>
                <div v-else-if="filteredProducts.length === 0" class="p-4 text-center text-gray-500">
                  Товары не найдены
                </div>
                <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
                  <label
                    v-for="product in filteredProducts"
                    :key="product.id"
                    class="flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      :value="product.id"
                      v-model="form.product_ids"
                      class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <div class="flex-1 flex items-center gap-3">
                      <div
                        v-if="product.image_url"
                        class="w-12 h-12 rounded-lg bg-gray-200 dark:bg-gray-700 overflow-hidden"
                      >
                        <img
                          :src="product.image_url"
                          :alt="product.name"
                          class="w-full h-full object-cover"
                        />
                      </div>
                      <Icon
                        v-else
                        icon="mdi:food"
                        class="w-8 h-8 text-gray-400"
                      />
                      <div class="flex-1">
                        <p class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ product.name || product.product_name }}
                        </p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">
                          {{ product.price }} ₸
                        </p>
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Выбрано товаров: {{ form.product_ids.length }}
              </p>
            </div>
          </form>
        </div>

        <!-- Modal Footer (закреплён, не скроллится) -->
        <div class="flex-shrink-0 p-6 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-b-xl">
          <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {{ error }}
          </div>
          <div class="flex items-center justify-end gap-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              form="fast-menu-group-form"
              :disabled="saving"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { Icon } from '@iconify/vue'
import fastMenuService from '@/services/fast-menu.service'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { normalizeMediaUrl } from '@/utils/mediaUrl'

const authStore = useAuthStore()

const groups = ref([])
const products = ref([])
const loading = ref(false)
const loadingProducts = ref(false)
const saving = ref(false)
const error = ref(null)
const showModal = ref(false)
const editingGroup = ref(null)
const productSearch = ref('')
const imageFileRef = ref(null)
const imagePreviewUrl = ref(null)

const form = reactive({
  name: '',
  order: 0,
  is_active: true,
  product_ids: []
})

const filteredProducts = computed(() => {
  if (!productSearch.value) {
    return products.value
  }
  const search = productSearch.value.toLowerCase()
  return products.value.filter(
    p => (p.name || p.product_name || '').toLowerCase().includes(search)
  )
})

const displayImageUrl = computed(() => {
  const url = imagePreviewUrl.value
  if (!url) return ''
  return url.startsWith('blob:') ? url : (normalizeMediaUrl(url) || url)
})

onMounted(async () => {
  await Promise.all([fetchGroups(), fetchProducts()])
})

const fetchGroups = async () => {
  loading.value = true
  error.value = null
  try {
    groups.value = await fastMenuService.getGroups()
  } catch (err) {
    error.value = 'Ошибка при загрузке групп'
    console.error('Failed to fetch groups:', err)
  } finally {
    loading.value = false
  }
}

const fetchProducts = async () => {
  loadingProducts.value = true
  try {
    // Только блюда из активного меню (в быстрое меню добавляем только их)
    const response = await api.get('/products/')
    const raw = response.data?.results ?? response.data
    products.value = Array.isArray(raw) ? raw : []
  } catch (err) {
    console.error('Failed to fetch products:', err)
    products.value = []
  } finally {
    loadingProducts.value = false
  }
}

function clearImagePreview() {
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = null
  if (imageFileRef.value) imageFileRef.value.value = ''
}

function onImageChange(event) {
  const file = event.target?.files?.[0]
  // Сначала отзываем старый blob-URL, чтобы не утекала память
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = null
  if (file) {
    imagePreviewUrl.value = URL.createObjectURL(file)
  } else {
    if (imageFileRef.value) imageFileRef.value.value = ''
  }
}

const openCreateModal = () => {
  editingGroup.value = null
  form.name = ''
  form.order = 0
  form.is_active = true
  form.product_ids = []
  productSearch.value = ''
  clearImagePreview()
  showModal.value = true
}

function getGroupImageUrl(group) {
  if (!group) return null
  const url = group.image_url ?? group.image
  return normalizeMediaUrl(url) || null
}

const openEditModal = async (group) => {
  editingGroup.value = group
  form.name = group.name
  form.order = group.order
  form.is_active = group.is_active
  clearImagePreview()
  imagePreviewUrl.value = getGroupImageUrl(group)

  // Загружаем детали группы для получения списка товаров и актуального image_url
  try {
    const groupDetails = await fastMenuService.getGroup(group.id)
    form.product_ids = groupDetails.items.map(item => item.product.id || item.product.product_id)
    const detailsImageUrl = getGroupImageUrl(groupDetails)
    if (detailsImageUrl) {
      imagePreviewUrl.value = detailsImageUrl
    }
  } catch (err) {
    console.error('Failed to fetch group details:', err)
    form.product_ids = []
  }

  productSearch.value = ''
  showModal.value = true
}

const closeModal = () => {
  clearImagePreview()
  showModal.value = false
  editingGroup.value = null
  error.value = null
}

const saveGroup = async () => {
  saving.value = true
  error.value = null
  const imageFile = imageFileRef.value?.files?.[0]

  try {
    if (imageFile) {
      const formData = new FormData()
      formData.append('name', form.name)
      formData.append('order', String(form.order))
      formData.append('is_active', form.is_active ? 'true' : 'false')
      const org = authStore.user?.organization
      const orgId = org != null && typeof org === 'object' ? (org.id ?? org.org_id) : org
      if (orgId) {
        formData.append('organization', String(orgId))
      }
      formData.append('image', imageFile)

      if (editingGroup.value) {
        await api.patch(`/fast-menu-groups/${editingGroup.value.id}/`, formData)
        await fastMenuService.updateGroupItems(editingGroup.value.id, form.product_ids)
      } else {
        const response = await api.post('/fast-menu-groups/', formData)
        const newGroup = response.data
        await fastMenuService.updateGroupItems(newGroup.id, form.product_ids)
      }
    } else {
      const groupData = {
        name: form.name,
        order: form.order,
        is_active: form.is_active,
        organization: authStore.user?.organization || null
      }
      if (editingGroup.value) {
        await fastMenuService.updateGroup(editingGroup.value.id, groupData)
        await fastMenuService.updateGroupItems(editingGroup.value.id, form.product_ids)
      } else {
        const newGroup = await fastMenuService.createGroup(groupData)
        await fastMenuService.updateGroupItems(newGroup.id, form.product_ids)
      }
    }

    await fetchGroups()
    closeModal()
  } catch (err) {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      if (data.detail) {
        error.value = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      } else {
        const parts = []
        for (const [key, val] of Object.entries(data)) {
          const msg = Array.isArray(val) ? val.join(' ') : String(val)
          if (msg) parts.push(`${key}: ${msg}`)
        }
        error.value = parts.length ? parts.join('; ') : (err.message || 'Ошибка при сохранении группы')
      }
    } else {
      error.value = err.message || 'Ошибка при сохранении группы'
    }
    console.error('Failed to save group:', err, data)
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (group) => {
  if (confirm(`Вы уверены, что хотите удалить группу "${group.name}"?`)) {
    try {
      await fastMenuService.deleteGroup(group.id)
      await fetchGroups()
    } catch (err) {
      error.value = 'Ошибка при удалении группы'
      console.error('Failed to delete group:', err)
    }
  }
}
</script>
