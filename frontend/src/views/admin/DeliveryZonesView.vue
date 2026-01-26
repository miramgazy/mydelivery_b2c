<template>
  <div class="max-w-full">
    <!-- Header with controls -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm mb-6">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Зоны доставки</h2>
          <div class="flex items-center gap-4 flex-wrap">
            <!-- Terminal Select -->
            <div class="flex items-center gap-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Терминал:</label>
              <select
                v-model="selectedTerminalId"
                @change="onTerminalChange"
                class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :disabled="loading || terminals.length === 0"
              >
                <option value="">Выберите терминал</option>
                <option
                  v-for="terminal in terminals"
                  :key="terminal.id"
                  :value="terminal.id"
                >
                  {{ terminal.name || terminal.terminal_group_name }}
                </option>
              </select>
            </div>

            <!-- City Select -->
            <div class="flex items-center gap-2">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Город:</label>
              <select
                v-model="selectedCityId"
                @change="onCityChange"
                class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :disabled="loading || cities.length === 0"
              >
                <option value="">Выберите город</option>
                <option
                  v-for="city in cities"
                  :key="city.id"
                  :value="city.id"
                >
                  {{ city.name }}
                </option>
              </select>
            </div>

            <!-- Add Zone Button -->
            <button
              @click="startDrawingZone"
              :disabled="!selectedTerminalId || isDrawing"
              class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700
                     text-white font-medium rounded-lg transition-colors disabled:opacity-50
                     disabled:cursor-not-allowed"
            >
              <Icon icon="mdi:map-marker-plus" class="w-5 h-5" />
              Добавить новую зону
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-if="successMessage" class="mx-6 mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
        <div class="flex items-center gap-2 text-green-800 dark:text-green-200">
          <Icon icon="mdi:check-circle" class="w-5 h-5" />
          <span>{{ successMessage }}</span>
        </div>
      </div>

      <div v-if="error" class="mx-6 mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
          <Icon icon="mdi:alert-circle" class="w-5 h-5" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Empty zones notification -->
      <div
        v-if="selectedTerminalId && !loading && (!zones || zones.length === 0) && !isDrawing"
        class="mx-6 mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-blue-800 dark:text-blue-200 text-sm">
          <Icon icon="mdi:information" class="w-5 h-5 flex-shrink-0" />
          <span>На этом терминале не настроены зоны доставки. Нажмите "Добавить новую зону" для создания первой зоны.</span>
        </div>
      </div>
    </div>

    <!-- Map Container -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
      <div id="map" class="w-full" style="height: 600px;"></div>
    </div>

    <!-- Save Button -->
    <div class="mt-6 flex justify-end">
      <button
        @click="saveZones"
        :disabled="!selectedTerminalId || saving || zones.length === 0"
        class="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700
               text-white font-medium rounded-lg transition-colors disabled:opacity-50
               disabled:cursor-not-allowed"
      >
        <Icon
          :icon="saving ? 'mdi:loading' : 'mdi:content-save'"
          :class="{ 'animate-spin': saving }"
          class="w-5 h-5"
        />
        {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
      </button>
    </div>

    <!-- Zone Edit Modal -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeEditModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full mx-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Настройки зоны</h3>
        </div>

        <div class="p-6 space-y-4">
          <!-- Zone Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Название зоны
            </label>
            <input
              v-model="editingZone.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Например: Центральная зона"
            />
          </div>

          <!-- Priority -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Приоритет
            </label>
            <input
              v-model.number="editingZone.priority"
              type="number"
              min="1"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Color -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Цвет
            </label>
            <div class="flex items-center gap-4">
              <input
                v-model="editingZone.color"
                type="color"
                class="w-20 h-10 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer"
              />
              <input
                v-model="editingZone.color"
                type="text"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="#FF0000"
              />
            </div>
          </div>

          <!-- Delivery Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тип доставки
            </label>
            <select
              v-model="editingZone.delivery_type"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="free">Бесплатная</option>
              <option value="paid">Платная</option>
            </select>
          </div>

          <!-- Delivery Cost (if paid) -->
          <div v-if="editingZone.delivery_type === 'paid'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Стоимость доставки
            </label>
            <input
              v-model.number="editingZone.delivery_cost"
              type="number"
              min="0"
              step="0.01"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="0.00"
            />
          </div>
        </div>

        <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button
            @click="closeEditModal"
            class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Отмена
          </button>
          <button
            @click="saveZoneSettings"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import organizationService from '@/services/organization.service'

// Data
const terminals = ref([])
const cities = ref([])
const selectedTerminalId = ref('')
const selectedCityId = ref('')
const zones = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const successMessage = ref('')

// Map state
let map = null
let mapObjects = []
let drawingManager = null
let currentPolygon = null
let currentZoneIndex = null
const isDrawing = ref(false)

// Modal state
const showEditModal = ref(false)
const editingZone = ref({
  name: '',
  priority: 1,
  color: '#FF0000',
  delivery_type: 'free',
  delivery_cost: 0
})

// Load terminals
const loadTerminals = async () => {
  try {
    loading.value = true
    const data = await organizationService.getTerminals()
    terminals.value = data
  } catch (err) {
    console.error('Failed to load terminals:', err)
    error.value = 'Не удалось загрузить терминалы'
  } finally {
    loading.value = false
  }
}

// Load cities
const loadCities = async () => {
  try {
    const data = await organizationService.getCities()
    cities.value = data
  } catch (err) {
    console.error('Failed to load cities:', err)
  }
}

// Load zones for selected terminal
const loadZones = async () => {
  if (!selectedTerminalId.value) {
    zones.value = []
    clearMap()
    return
  }

  try {
    loading.value = true
    const terminal = terminals.value.find(t => t.id === selectedTerminalId.value)
    if (terminal && terminal.delivery_zones_conditions) {
      zones.value = terminal.delivery_zones_conditions || []
      displayZonesOnMap()
    } else {
      zones.value = []
      clearMap()
    }
  } catch (err) {
    console.error('Failed to load zones:', err)
    error.value = 'Не удалось загрузить зоны доставки'
  } finally {
    loading.value = false
  }
}

// Initialize Yandex Map
const initMap = () => {
  if (typeof ymaps === 'undefined') {
    console.error('Yandex Maps API not loaded')
    return
  }

  ymaps.ready(() => {
    // Default center (Almaty)
    const defaultCenter = [43.2220, 76.8512]
    
    map = new ymaps.Map('map', {
      center: defaultCenter,
      zoom: 12,
      controls: ['zoomControl', 'fullscreenControl']
    })
    
    // If city selected, center map on it
    if (selectedCityId.value) {
      const city = cities.value.find(c => c.id === selectedCityId.value)
      if (city) {
        centerMapOnCity(city)
      }
    }
  })
}

// Display zones on map
const displayZonesOnMap = () => {
  clearMap()
  
  zones.value.forEach((zone, index) => {
    if (!zone.coordinates || zone.coordinates.length === 0) return

    const polygon = new ymaps.Polygon(
      [zone.coordinates],
      {
        zoneIndex: index,
        zoneName: zone.name || `Зона ${index + 1}`,
        zonePriority: zone.priority || 1
      },
      {
        fillColor: zone.color || '#FF0000',
        fillOpacity: 0.3,
        strokeColor: zone.color || '#FF0000',
        strokeWidth: 2,
        strokeOpacity: 0.8
      }
    )

    // Add label in center
    const bounds = polygon.geometry.getBounds()
    const center = bounds ? [
      (bounds[0][0] + bounds[1][0]) / 2,
      (bounds[0][1] + bounds[1][1]) / 2
    ] : zone.coordinates[0]

    // Create label with text
    const label = new ymaps.Placemark(
      center,
      {
        balloonContent: `${zone.name || `Зона ${index + 1}`}<br/>Приоритет: ${zone.priority || 1}`
      },
      {
        iconLayout: 'default#imageWithContent',
        iconImageHref: 'data:image/svg+xml;base64,' + btoa(`
          <svg width="60" height="60" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="25" fill="white" stroke="#000" stroke-width="2"/>
            <text x="30" y="25" font-size="10" font-weight="bold" text-anchor="middle" fill="#000">${(zone.name || `Зона ${index + 1}`).substring(0, 8)}</text>
            <text x="30" y="38" font-size="10" text-anchor="middle" fill="#000">${zone.priority || 1}</text>
          </svg>
        `),
        iconImageSize: [60, 60],
        iconImageOffset: [-30, -30]
      }
    )
    
    label.properties.set('iconContent', `${zone.name || index + 1}<br/>${zone.priority || 1}`)

    polygon.properties.set('zoneIndex', index)
    polygon.events.add('click', () => editZone(index))

    map.geoObjects.add(polygon)
    map.geoObjects.add(label)
    
    mapObjects.push(polygon)
    mapObjects.push(label)
  })
}

// Clear map
const clearMap = () => {
  if (map && map.geoObjects) {
    mapObjects.forEach(obj => map.geoObjects.remove(obj))
    mapObjects = []
  }
}

// Start drawing new zone
const startDrawingZone = () => {
  if (!map) {
    error.value = 'Карта не инициализирована'
    return
  }

  isDrawing.value = true
  error.value = ''

  // Create new polygon
  const newZone = {
    name: `Зона ${zones.value.length + 1}`,
    priority: zones.value.length + 1,
    color: '#FF0000',
    delivery_type: 'free',
    delivery_cost: 0,
    coordinates: []
  }

  // Create temporary polygon
  currentPolygon = new ymaps.Polygon([], {
    fillColor: newZone.color,
    fillOpacity: 0.3,
    strokeColor: newZone.color,
    strokeWidth: 2
  }, {
    editorDrawingCursor: 'crosshair',
    editorMaxPoints: Infinity
  })

  map.geoObjects.add(currentPolygon)
  
  // Enable drawing mode
  const editor = new ymaps.polygon.PolygonEditor(map, currentPolygon)
  editor.startDrawing()
  
  // Track drawing state
  let drawingComplete = false
  
  // On drawing complete
  editor.events.add('drawingstop', () => {
    if (drawingComplete) return
    drawingComplete = true
    
    const coordinates = currentPolygon.geometry.getCoordinates()
    if (coordinates && coordinates.length > 0 && coordinates[0].length >= 3) {
      newZone.coordinates = coordinates[0]
      zones.value.push(newZone)
      currentZoneIndex = zones.value.length - 1
      editor.stopDrawing()
      closeDrawing()
      showEditModal.value = true
      editingZone.value = { ...newZone }
      displayZonesOnMap()
    } else {
      error.value = 'Зона должна содержать минимум 3 точки'
      map.geoObjects.remove(currentPolygon)
      editor.stopDrawing()
      closeDrawing()
    }
  })
  
  // Handle escape key
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && isDrawing.value) {
      if (currentPolygon) {
        map.geoObjects.remove(currentPolygon)
      }
      editor.stopDrawing()
      closeDrawing()
      document.removeEventListener('keydown', handleKeyDown)
    }
  }
  document.addEventListener('keydown', handleKeyDown)
}

// Close drawing
const closeDrawing = () => {
  isDrawing.value = false
  if (currentPolygon) {
    // Don't remove if zone was saved
    if (currentZoneIndex === null || !zones.value[currentZoneIndex]) {
      map.geoObjects.remove(currentPolygon)
    }
    currentPolygon = null
  }
}

// Edit zone
const editZone = (index) => {
  if (index < 0 || index >= zones.value.length) return
  
  currentZoneIndex = index
  editingZone.value = { ...zones.value[index] }
  showEditModal.value = true
}

// Save zone settings
const saveZoneSettings = () => {
  if (!editingZone.value.name) {
    error.value = 'Название зоны обязательно'
    return
  }

  if (currentZoneIndex !== null && currentZoneIndex >= 0 && currentZoneIndex < zones.value.length) {
    zones.value[currentZoneIndex] = { ...editingZone.value }
    displayZonesOnMap()
  }

  closeEditModal()
}

// Close edit modal
const closeEditModal = () => {
  showEditModal.value = false
  editingZone.value = {
    name: '',
    priority: 1,
    color: '#FF0000',
    delivery_type: 'free',
    delivery_cost: 0
  }
  currentZoneIndex = null
}

// Save zones to backend
const saveZones = async () => {
  if (!selectedTerminalId.value) {
    error.value = 'Выберите терминал'
    return
  }

  try {
    saving.value = true
    error.value = ''
    successMessage.value = ''

    // Prepare zones data
    const zonesData = zones.value.map(zone => ({
      name: zone.name,
      priority: zone.priority || 1,
      color: zone.color || '#FF0000',
      delivery_type: zone.delivery_type || 'free',
      delivery_cost: zone.delivery_cost || 0,
      coordinates: zone.coordinates || []
    }))

    await organizationService.updateTerminalDeliveryZones(selectedTerminalId.value, zonesData)
    
    successMessage.value = 'Зоны доставки успешно сохранены'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    console.error('Failed to save zones:', err)
    error.value = err.response?.data?.error || 'Не удалось сохранить зоны доставки'
  } finally {
    saving.value = false
  }
}

// Terminal change handler
const onTerminalChange = () => {
  // Set city from terminal if available
  if (selectedTerminalId.value) {
    const terminal = terminals.value.find(t => t.id === selectedTerminalId.value)
    if (terminal) {
      // Try to find city by city_id or city field
      let city = null
      if (terminal.city_id) {
        city = cities.value.find(c => c.id === terminal.city_id)
      } else if (terminal.city) {
        // If city is an object with id
        const cityId = typeof terminal.city === 'object' ? terminal.city.id : terminal.city
        city = cities.value.find(c => c.id === cityId)
      }
      
      if (city) {
        selectedCityId.value = city.id
        // Center map on city after a short delay to ensure map is ready
        setTimeout(() => {
          centerMapOnCity(city)
        }, 200)
      } else if (terminal.city_name) {
        // If we have city name but not ID, try to find by name
        city = cities.value.find(c => c.name === terminal.city_name)
        if (city) {
          selectedCityId.value = city.id
          setTimeout(() => {
            centerMapOnCity(city)
          }, 200)
        }
      }
    }
  }
  loadZones()
}

// Center map on city
const centerMapOnCity = (city) => {
  if (!map || typeof ymaps === 'undefined') {
    return
  }

  if (typeof ymaps.ready === 'function') {
    ymaps.ready(() => {
      if (!map) return
      
      const geocoder = ymaps.geocode(city.name)
      geocoder.then((res) => {
        const firstGeoObject = res.geoObjects.get(0)
        if (firstGeoObject && map) {
          const coords = firstGeoObject.geometry.getCoordinates()
          map.setCenter(coords, 12)
        }
      }).catch(() => {
        // Ignore geocoding errors
      })
    })
  } else {
    // If ymaps is already loaded
    const geocoder = ymaps.geocode(city.name)
    geocoder.then((res) => {
      const firstGeoObject = res.geoObjects.get(0)
      if (firstGeoObject && map) {
        const coords = firstGeoObject.geometry.getCoordinates()
        map.setCenter(coords, 12)
      }
    }).catch(() => {
      // Ignore geocoding errors
    })
  }
}

// City change handler
const onCityChange = () => {
  if (selectedCityId.value) {
    const city = cities.value.find(c => c.id === selectedCityId.value)
    if (city) {
      centerMapOnCity(city)
    }
  }
}

// Load Yandex Maps script
const loadYandexMaps = () => {
  if (typeof ymaps !== 'undefined') {
    initMap()
    return
  }

  // Check if script already exists
  if (document.querySelector('script[src*="api-maps.yandex.ru"]')) {
    // Wait for it to load
    const checkInterval = setInterval(() => {
      if (typeof ymaps !== 'undefined') {
        clearInterval(checkInterval)
        initMap()
      }
    }, 100)
    return
  }

  const script = document.createElement('script')
  script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU'
  script.async = true
  script.onload = () => {
    initMap()
  }
  script.onerror = () => {
    error.value = 'Не удалось загрузить Yandex Maps API'
  }
  document.head.appendChild(script)
}

onMounted(async () => {
  await loadTerminals()
  await loadCities()
  loadYandexMaps()
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})
</script>
