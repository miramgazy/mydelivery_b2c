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

            <!-- Refresh Button -->
            <button
              @click="refreshZones"
              :disabled="!selectedTerminalId || loading"
              class="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700
                     text-white font-medium rounded-lg transition-colors disabled:opacity-50
                     disabled:cursor-not-allowed"
            >
              <Icon
                :icon="loading ? 'mdi:loading' : 'mdi:refresh'"
                :class="{ 'animate-spin': loading }"
                class="w-5 h-5"
              />
              Обновить
            </button>

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

          <!-- Color Picker (like in example) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Цвет отображения
            </label>
            <div class="flex gap-2">
              <button
                type="button"
                @click="editingZone.color = 'green'"
                :class="[
                  'flex-1 h-10 rounded-lg border-2 transition-all font-semibold text-xs text-white',
                  editingZone.color === 'green'
                    ? 'border-gray-900 dark:border-white opacity-100 scale-105'
                    : 'border-transparent opacity-70 hover:opacity-90'
                ]"
                style="background: #2ecc71;"
              >
                Зеленый
              </button>
              <button
                type="button"
                @click="editingZone.color = 'purple'"
                :class="[
                  'flex-1 h-10 rounded-lg border-2 transition-all font-semibold text-xs text-white',
                  editingZone.color === 'purple'
                    ? 'border-gray-900 dark:border-white opacity-100 scale-105'
                    : 'border-transparent opacity-70 hover:opacity-90'
                ]"
                style="background: #8e44ad;"
              >
                Фиолетовый
              </button>
              <button
                type="button"
                @click="editingZone.color = 'red'"
                :class="[
                  'flex-1 h-10 rounded-lg border-2 transition-all font-semibold text-xs text-white',
                  editingZone.color === 'red'
                    ? 'border-gray-900 dark:border-white opacity-100 scale-105'
                    : 'border-transparent opacity-70 hover:opacity-90'
                ]"
                style="background: #e74c3c;"
              >
                Красный
              </button>
            </div>
          </div>

          <!-- Delivery Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тип доставки
            </label>
            <div class="flex gap-2 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
              <button
                type="button"
                @click="editingZone.delivery_type = 'free'"
                :class="[
                  'flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-colors',
                  editingZone.delivery_type === 'free'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
              >
                Бесплатная
              </button>
              <button
                type="button"
                @click="editingZone.delivery_type = 'paid'"
                :class="[
                  'flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-colors',
                  editingZone.delivery_type === 'paid'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                ]"
              >
                Платная
              </button>
            </div>
          </div>

          <!-- Min Order Amount (if free) -->
          <div v-if="editingZone.delivery_type === 'free'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Минимальная сумма заказа (₸)
            </label>
            <input
              v-model.number="editingZone.min_order_amount"
              type="number"
              min="0"
              step="0.01"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="0.00"
            />
          </div>

          <!-- Delivery Cost (if paid) -->
          <div v-if="editingZone.delivery_type === 'paid'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Стоимость доставки (₸)
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

        <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between gap-3">
          <!-- Delete button (only for existing zones, not new ones - same as example) -->
          <button
            v-if="currentZoneIndex !== null && currentZoneIndex >= 0 && currentZoneIndex < zones.length && !isNewZone"
            @click="deleteZone"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Icon icon="mdi:delete" class="w-5 h-5" />
            Удалить
          </button>
          <div v-else class="flex-1"></div>
          
          <div class="flex gap-3">
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
const isNewZone = ref(false) // Track if we're editing a new zone

// Modal state
const showEditModal = ref(false)
const editingZone = ref({
  name: '',
  priority: 1,
  color: 'red', // Use color name instead of hex (like in example)
  delivery_type: 'free',
  delivery_cost: 0,
  min_order_amount: 0,
  coordinates: []
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
const loadZones = async (forceRefresh = false) => {
  if (!selectedTerminalId.value) {
    zones.value = []
    clearMap()
    return
  }

  try {
    loading.value = true
    error.value = ''
    successMessage.value = ''
    
    // Reload terminals to get fresh data from database
    const data = await organizationService.getTerminals()
    terminals.value = data
    
    const terminal = terminals.value.find(t => t.id === selectedTerminalId.value)
    
    if (!terminal) {
      error.value = 'Терминал не найден'
      zones.value = []
      clearMap()
      return
    }
    
    // Check if delivery_zones_conditions exists and is valid
    const zonesData = terminal.delivery_zones_conditions
    
    console.log('Loaded zones data from terminal:', zonesData)
    
    if (zonesData && Array.isArray(zonesData) && zonesData.length > 0) {
      // Validate and normalize zones data
      // Handle both 'coordinates' and 'coords' formats (from example)
      const validZones = zonesData
        .filter(zone => {
          if (!zone || typeof zone !== 'object') {
            console.warn('Invalid zone object:', zone)
            return false
          }
          
          // Check for both 'coordinates' and 'coords' (example uses 'coords')
          const coords = zone.coordinates || zone.coords
          if (!coords || !Array.isArray(coords)) {
            console.warn('Zone missing coordinates/coords:', zone)
            return false
          }
          if (coords.length < 3) {
            console.warn('Zone has less than 3 coordinates:', coords.length, zone)
            return false
          }
          return true
        })
        .map(zone => {
          // Normalize coordinates (handle both formats)
          const coords = zone.coordinates || zone.coords || []
          
          // Normalize color to standard format (green, purple, red)
          let normalizedColor = zone.color || 'red'
          if (typeof normalizedColor === 'string') {
            const colorLower = normalizedColor.toLowerCase()
            if (colorLower.includes('green') || colorLower === '#2ecc71' || colorLower === '#27ae60') {
              normalizedColor = 'green'
            } else if (colorLower.includes('purple') || colorLower === '#9b59b6' || colorLower === '#8e44ad') {
              normalizedColor = 'purple'
            } else if (colorLower.includes('red') || colorLower === '#e74c3c' || colorLower === '#c0392b' || colorLower === '#ff0000' || colorLower === '#f00') {
              normalizedColor = 'red'
            } else {
              normalizedColor = 'red' // Default
            }
          } else {
            normalizedColor = 'red'
          }
          
          return {
            name: zone.name || `Зона`,
            priority: zone.priority || 1,
            color: normalizedColor,
            delivery_type: zone.delivery_type || 'free',
            delivery_cost: zone.delivery_type === 'paid' ? (zone.delivery_cost || zone.price || 0) : 0,
            min_order_amount: zone.delivery_type === 'free' ? (zone.min_order_amount || zone.minSum || 0) : 0,
            coordinates: coords
          }
        })
      
      console.log('Valid zones after normalization:', validZones)
      
      zones.value = validZones
      
      if (validZones.length > 0) {
        successMessage.value = `Загружено зон: ${validZones.length}`
        setTimeout(() => {
          successMessage.value = ''
        }, 2000)
      }
      
      // Wait for map to be ready before displaying zones
      const displayZones = () => {
        console.log('Attempting to display zones, map ready:', !!map, 'ymaps ready:', typeof ymaps !== 'undefined')
        if (map && typeof ymaps !== 'undefined') {
          try {
            // Use ymaps.ready to ensure API is fully loaded
            if (typeof ymaps.ready === 'function') {
              ymaps.ready(() => {
                console.log('Ymaps ready, displaying zones')
                displayZonesOnMap()
              })
            } else {
              console.log('Ymaps already ready, displaying zones')
              displayZonesOnMap()
            }
          } catch (err) {
            console.error('Error displaying zones on map:', err)
            error.value = 'Ошибка при отображении зон на карте: ' + err.message
          }
        } else {
          console.warn('Map not ready for displaying zones', { map: !!map, ymaps: typeof ymaps })
        }
      }
      
      // Ensure map is ready
      if (map && typeof ymaps !== 'undefined') {
        // Map is ready, display zones
        setTimeout(displayZones, 200)
      } else {
        // If map is not ready, wait a bit and try again
        console.log('Waiting for map to be ready...')
        let attempts = 0
        const maxAttempts = 50 // 5 seconds max
        
        const checkMap = setInterval(() => {
          attempts++
          if (map && typeof ymaps !== 'undefined') {
            clearInterval(checkMap)
            console.log('Map ready after', attempts, 'attempts')
            displayZones()
          } else if (attempts >= maxAttempts) {
            clearInterval(checkMap)
            error.value = 'Карта не инициализирована. Попробуйте обновить страницу.'
            console.error('Map initialization timeout')
          }
        }, 100)
      }
    } else {
      // No zones or empty array
      zones.value = []
      clearMap()
      if (forceRefresh) {
        successMessage.value = 'Зоны доставки не найдены'
        setTimeout(() => {
          successMessage.value = ''
        }, 2000)
      }
    }
  } catch (err) {
    console.error('Failed to load zones:', err)
    error.value = err.response?.data?.error || err.message || 'Не удалось загрузить зоны доставки'
    zones.value = []
    clearMap()
  } finally {
    loading.value = false
  }
}

// Refresh zones from database
const refreshZones = async () => {
  await loadZones(true)
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
        // Use setTimeout to ensure map is fully initialized
        setTimeout(() => {
          centerMapOnCity(city)
        }, 300)
      }
    }
  })
}

// Sync label for polygon (similar to example)
const syncLabel = (polygon, zoneIndex) => {
  try {
    let label = polygon.properties.get('labelObj')
    const coords = polygon.geometry.getCoordinates()
    if (!coords || coords.length === 0 || !coords[0] || coords[0].length < 3) return

    // Calculate center of polygon
    let lat = 0, lng = 0
    coords[0].forEach(c => {
      lat += c[0]
      lng += c[1]
    })
    const center = [lat / coords[0].length, lng / coords[0].length]

    // Get zone data
    const zone = zones.value[zoneIndex]
    const name = zone?.name || polygon.properties.get('name') || `Зона ${zoneIndex + 1}`
    const priority = zone?.priority || polygon.properties.get('priority') || 1
    const content = `${name} (Pr:${priority})`

    if (!label) {
      // Create new label
      label = new ymaps.Placemark(
        center,
        { iconContent: content },
        {
          preset: 'islands#blackStretchyIcon',
          zIndex: 1000
        }
      )
      label.events.add('click', () => editZone(zoneIndex))
      map.geoObjects.add(label)
      polygon.properties.set('labelObj', label)
      mapObjects.push(label)
    } else {
      // Update existing label
      label.geometry.setCoordinates(center)
      label.properties.set('iconContent', content)
    }
  } catch (err) {
    console.error('Error syncing label:', err)
  }
}

// Display zones on map (similar to import logic in example)
const displayZonesOnMap = () => {
  if (!map || typeof ymaps === 'undefined') {
    console.warn('Map is not initialized, cannot display zones')
    return
  }

  // Clear existing zones
  if (!isDrawing.value) {
    clearMap()
  }
  
  if (!zones.value || zones.value.length === 0) {
    console.log('No zones to display')
    return
  }
  
  console.log('Displaying zones:', zones.value.length)
  
  // Color mapping (exactly as in example)
  const COLORS = {
    green: { fill: '#2ecc7155', stroke: '#27ae60' },
    purple: { fill: '#9b59b655', stroke: '#8e44ad' },
    red: { fill: '#e74c3c55', stroke: '#c0392b' }
  }
  
  zones.value.forEach((zone, index) => {
    try {
      // Validate zone data
      if (!zone || !zone.coordinates || !Array.isArray(zone.coordinates) || zone.coordinates.length < 3) {
        console.warn(`Zone ${index} has invalid coordinates:`, zone)
        return
      }

      // Skip if this is the current polygon being drawn
      if (currentPolygon && index === currentZoneIndex) {
        return
      }

      // Determine color (normalize to color name)
      let colorKey = zone.color || 'red'
      
      // Normalize color: convert hex or any variation to standard color name
      if (typeof colorKey === 'string') {
        const colorLower = colorKey.toLowerCase()
        if (colorLower.includes('green') || colorLower === '#2ecc71' || colorLower === '#27ae60') {
          colorKey = 'green'
        } else if (colorLower.includes('purple') || colorLower === '#9b59b6' || colorLower === '#8e44ad') {
          colorKey = 'purple'
        } else if (colorLower.includes('red') || colorLower === '#e74c3c' || colorLower === '#c0392b' || colorLower === '#ff0000' || colorLower === '#f00') {
          colorKey = 'red'
        } else {
          // Default to red if unknown color
          colorKey = 'red'
        }
      } else {
        colorKey = 'red'
      }
      
      const colorStyle = COLORS[colorKey] || COLORS.red
      
      console.log(`Zone ${index} color: ${zone.color} -> normalized: ${colorKey}`, colorStyle)

      // Create polygon (same as example import logic)
      const poly = new ymaps.Polygon(
        [zone.coordinates], // Coordinates as first argument
        {}, // Empty properties object
        {
          fillColor: colorStyle.fill,
          strokeColor: colorStyle.stroke,
          strokeWidth: 2,
          fillOpacity: 0.3
        }
      )

      // Set all zone properties (same as example)
      poly.properties.set({
        name: zone.name || `Зона ${index + 1}`,
        priority: zone.priority || 1,
        color: colorKey, // Store normalized color name
        isFree: zone.delivery_type === 'free',
        minSum: zone.delivery_type === 'free' ? (zone.min_order_amount || 0) : 0,
        price: zone.delivery_type === 'paid' ? (zone.delivery_cost || 0) : 0,
        delivery_type: zone.delivery_type || 'free',
        delivery_cost: zone.delivery_type === 'paid' ? (zone.delivery_cost || 0) : 0,
        min_order_amount: zone.delivery_type === 'free' ? (zone.min_order_amount || 0) : 0,
        zoneIndex: index // Store index for deletion
      })
      
      console.log(`Zone ${index} created with color: ${colorKey}`, colorStyle)

      // Add to map
      map.geoObjects.add(poly)
      
      // Enable editing
      poly.editor.startEditing()
      
      // Sync label
      syncLabel(poly, index)

      // Add event handlers (same as example)
      poly.events.add('click', () => editZone(index))
      poly.geometry.events.add('change', () => syncLabel(poly, index))

      // Store in mapObjects
      mapObjects.push(poly)
      
      console.log(`Zone ${index} displayed successfully`)
    } catch (err) {
      console.error(`Error displaying zone ${index}:`, err, zone)
    }
  })
  
  console.log(`Total zones displayed: ${mapObjects.length}`)
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
  if (!map || typeof ymaps === 'undefined') {
    error.value = 'Карта не инициализирована'
    return
  }

  if (!selectedCityId.value) {
    error.value = 'Сначала выберите город!'
    return
  }

  isDrawing.value = true
  error.value = ''
  successMessage.value = 'Рисуйте зону. Нажмите ENTER для завершения.'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)

  // Create temporary polygon
  currentPolygon = new ymaps.Polygon([], {}, {
    strokeWidth: 2,
    strokeColor: '#000',
    fillColor: '#FF000055',
    fillOpacity: 0.3
  })

  map.geoObjects.add(currentPolygon)
  
  // Start drawing mode
  currentPolygon.editor.startDrawing()
  
  // Finish drawing on Enter key
  const finishHandler = (e) => {
    if (e.key === 'Enter' && isDrawing.value && currentPolygon) {
      currentPolygon.editor.stopDrawing()
      
      const coordinates = currentPolygon.geometry.getCoordinates()
      if (coordinates && coordinates.length > 0 && coordinates[0].length >= 3) {
        // Create new zone object
        const newZone = {
          name: `Зона ${zones.value.length + 1}`,
          priority: zones.value.length + 1,
          color: 'red', // Default color (like in example)
          delivery_type: 'free',
          delivery_cost: 0,
          min_order_amount: 0,
          coordinates: coordinates[0]
        }
        
        // Store polygon reference in zone for editing
        currentZoneIndex = zones.value.length
        zones.value.push(newZone)
        isNewZone.value = true // Mark as new zone
        
        // Open modal for editing
        editingZone.value = { ...newZone }
        showEditModal.value = true
        
        // Remove temporary handler
        window.removeEventListener('keydown', finishHandler)
        isDrawing.value = false
      } else {
        error.value = 'Зона должна содержать минимум 3 точки'
        map.geoObjects.remove(currentPolygon)
        currentPolygon = null
        window.removeEventListener('keydown', finishHandler)
        isDrawing.value = false
      }
    }
  }
  
  window.addEventListener('keydown', finishHandler)
  
  // Handle escape key to cancel
  const cancelHandler = (e) => {
    if (e.key === 'Escape' && isDrawing.value && currentPolygon) {
      map.geoObjects.remove(currentPolygon)
      currentPolygon = null
      window.removeEventListener('keydown', finishHandler)
      window.removeEventListener('keydown', cancelHandler)
      isDrawing.value = false
      successMessage.value = ''
    }
  }
  window.addEventListener('keydown', cancelHandler)
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
  isNewZone.value = false // Existing zone, not new
  const zone = zones.value[index]
  
  // Normalize color to standard format
  let normalizedColor = zone.color || 'red'
  if (typeof normalizedColor === 'string') {
    const colorLower = normalizedColor.toLowerCase()
    if (colorLower.includes('green') || colorLower === '#2ecc71' || colorLower === '#27ae60') {
      normalizedColor = 'green'
    } else if (colorLower.includes('purple') || colorLower === '#9b59b6' || colorLower === '#8e44ad') {
      normalizedColor = 'purple'
    } else if (colorLower.includes('red') || colorLower === '#e74c3c' || colorLower === '#c0392b' || colorLower === '#ff0000' || colorLower === '#f00') {
      normalizedColor = 'red'
    } else {
      normalizedColor = 'red' // Default
    }
  } else {
    normalizedColor = 'red'
  }
  
  editingZone.value = {
    name: zone.name || '',
    priority: zone.priority || 1,
    color: normalizedColor,
    delivery_type: zone.delivery_type || 'free',
    delivery_cost: zone.delivery_cost || 0,
    min_order_amount: zone.min_order_amount || 0,
    coordinates: zone.coordinates || []
  }
  showEditModal.value = true
}

// Save zone settings
const saveZoneSettings = () => {
  if (!editingZone.value.name || !editingZone.value.name.trim()) {
    error.value = 'Название зоны обязательно'
    return
  }

  // Ensure coordinates are preserved
  if (!editingZone.value.coordinates || editingZone.value.coordinates.length === 0) {
    if (currentZoneIndex !== null && zones.value[currentZoneIndex]) {
      editingZone.value.coordinates = zones.value[currentZoneIndex].coordinates
    } else if (currentPolygon) {
      const coords = currentPolygon.geometry.getCoordinates()
      if (coords && coords.length > 0) {
        editingZone.value.coordinates = coords[0]
      }
    }
  }

  if (currentZoneIndex !== null && currentZoneIndex >= 0 && currentZoneIndex < zones.value.length) {
    // Normalize color to standard format
    let normalizedColor = editingZone.value.color || 'red'
    if (typeof normalizedColor === 'string') {
      const colorLower = normalizedColor.toLowerCase()
      if (colorLower.includes('green') || colorLower === '#2ecc71' || colorLower === '#27ae60') {
        normalizedColor = 'green'
      } else if (colorLower.includes('purple') || colorLower === '#9b59b6' || colorLower === '#8e44ad') {
        normalizedColor = 'purple'
      } else if (colorLower.includes('red') || colorLower === '#e74c3c' || colorLower === '#c0392b' || colorLower === '#ff0000' || colorLower === '#f00') {
        normalizedColor = 'red'
      } else {
        normalizedColor = 'red' // Default
      }
    } else {
      normalizedColor = 'red'
    }
    
    // Update zone data with all fields
    const updatedZone = {
      name: editingZone.value.name.trim(),
      priority: editingZone.value.priority || 1,
      color: normalizedColor,
      delivery_type: editingZone.value.delivery_type || 'free',
      delivery_cost: editingZone.value.delivery_type === 'paid' ? (editingZone.value.delivery_cost || 0) : 0,
      min_order_amount: editingZone.value.delivery_type === 'free' ? (editingZone.value.min_order_amount || 0) : 0,
      coordinates: editingZone.value.coordinates || []
    }
    
    zones.value[currentZoneIndex] = updatedZone
    
    // If we have currentPolygon (newly drawn), update its properties and style
    if (currentPolygon) {
      // Color mapping (same as example)
      const COLORS = {
        green: { fill: '#2ecc7155', stroke: '#27ae60' },
        purple: { fill: '#9b59b655', stroke: '#8e44ad' },
        red: { fill: '#e74c3c55', stroke: '#c0392b' }
      }
      
      const colorStyle = COLORS[normalizedColor] || COLORS.red
      
      // Update visual style (same as example)
      currentPolygon.options.set({
        fillColor: colorStyle.fill,
        strokeColor: colorStyle.stroke
      })
      
      // Store zone index in polygon properties
      currentPolygon.properties.set('zoneIndex', currentZoneIndex)
      
      // Enable editing mode for the polygon
      currentPolygon.editor.startEditing()
      
      // Add click handler to edit zone
      currentPolygon.events.add('click', () => {
        editZone(currentZoneIndex)
      })
      
      currentPolygon = null
    }
    
    // Mark as existing zone after save
    isNewZone.value = false
    
    // Redraw all zones on map
    displayZonesOnMap()
    successMessage.value = 'Зона сохранена'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
    
    closeEditModal()
  } else {
    error.value = 'Ошибка: индекс зоны не найден'
  }
}

// Delete zone (similar to example)
const deleteZone = () => {
  if (currentZoneIndex === null || currentZoneIndex < 0 || currentZoneIndex >= zones.value.length) {
    error.value = 'Не удалось найти зону для удаления'
    return
  }

  // Confirm deletion (same as example)
  if (!confirm('Вы уверены, что хотите удалить эту зону?')) {
    return
  }

  try {
    // Find polygon and label for this zone
    let polygonToRemove = null
    let labelToRemove = null
    
    // Search in mapObjects for polygon with matching zoneIndex
    for (let i = 0; i < mapObjects.length; i++) {
      const obj = mapObjects[i]
      if (obj.properties && obj.properties.get('zoneIndex') === currentZoneIndex) {
        polygonToRemove = obj
        // Get label from polygon properties
        labelToRemove = obj.properties.get('labelObj')
        break
      }
    }
    
    // Remove from map (same as example)
    if (polygonToRemove && map && map.geoObjects) {
      map.geoObjects.remove(polygonToRemove)
      // Remove from mapObjects array
      const polygonIndex = mapObjects.indexOf(polygonToRemove)
      if (polygonIndex > -1) {
        mapObjects.splice(polygonIndex, 1)
      }
    }
    
    if (labelToRemove && map && map.geoObjects) {
      map.geoObjects.remove(labelToRemove)
      // Remove from mapObjects array
      const labelIndex = mapObjects.indexOf(labelToRemove)
      if (labelIndex > -1) {
        mapObjects.splice(labelIndex, 1)
      }
    }
    
    // Remove zone from array (same as example: polygons = polygons.filter(...))
    zones.value = zones.value.filter((_, index) => index !== currentZoneIndex)
    
    // Clear current references
    currentPolygon = null
    currentZoneIndex = null
    
    // Close modal
    closeEditModal()
    
    // Redraw zones to update indices
    displayZonesOnMap()
    
    successMessage.value = 'Зона удалена'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  } catch (err) {
    console.error('Error deleting zone:', err)
    error.value = 'Ошибка при удалении зоны: ' + err.message
  }
}

// Close edit modal
const closeEditModal = () => {
  // If closing modal without saving a new polygon, remove it
  if (currentPolygon && currentZoneIndex !== null) {
    const zone = zones.value[currentZoneIndex]
    // Check if zone was saved (has proper name, not default)
    const defaultName = `Зона ${currentZoneIndex + 1}`
    if (!zone || !zone.name || zone.name === defaultName || !zone.name.trim()) {
      if (map && map.geoObjects) {
        map.geoObjects.remove(currentPolygon)
      }
      zones.value.splice(currentZoneIndex, 1)
      currentPolygon = null
      displayZonesOnMap()
    }
  }
  
  showEditModal.value = false
  editingZone.value = {
    name: '',
    priority: 1,
    color: 'red',
    delivery_type: 'free',
    delivery_cost: 0,
    min_order_amount: 0,
    coordinates: []
  }
  currentZoneIndex = null
  isNewZone.value = false
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

    // Prepare zones data (normalize colors)
    const zonesData = zones.value.map(zone => {
      // Normalize color to standard format
      let normalizedColor = zone.color || 'red'
      if (typeof normalizedColor === 'string') {
        const colorLower = normalizedColor.toLowerCase()
        if (colorLower.includes('green') || colorLower === '#2ecc71' || colorLower === '#27ae60') {
          normalizedColor = 'green'
        } else if (colorLower.includes('purple') || colorLower === '#9b59b6' || colorLower === '#8e44ad') {
          normalizedColor = 'purple'
        } else if (colorLower.includes('red') || colorLower === '#e74c3c' || colorLower === '#c0392b' || colorLower === '#ff0000' || colorLower === '#f00') {
          normalizedColor = 'red'
        } else {
          normalizedColor = 'red' // Default
        }
      } else {
        normalizedColor = 'red'
      }
      
      return {
        name: zone.name,
        priority: zone.priority || 1,
        color: normalizedColor,
        delivery_type: zone.delivery_type || 'free',
        delivery_cost: zone.delivery_type === 'paid' ? (zone.delivery_cost || 0) : 0,
        min_order_amount: zone.delivery_type === 'free' ? (zone.min_order_amount || 0) : 0,
        coordinates: zone.coordinates || []
      }
    })

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
const onTerminalChange = async () => {
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
  // Load zones when terminal changes
  await loadZones(false)
}

// Center map on city
const centerMapOnCity = (city) => {
  if (!map || typeof ymaps === 'undefined') {
    return
  }

  // Try geocoding first
  if (typeof ymaps.geocode === 'function') {
    const geocoder = ymaps.geocode(city.name)
    geocoder.then((res) => {
      const firstGeoObject = res.geoObjects.get(0)
      if (firstGeoObject && map) {
        const coords = firstGeoObject.geometry.getCoordinates()
        map.setCenter(coords, 12)
      }
    }).catch(() => {
      // If geocoding fails, try known cities coordinates
      const knownCities = {
        'Алматы': [43.2220, 76.8512],
        'Алмата': [43.2220, 76.8512],
        'Астана': [51.1694, 71.4491],
        'Нур-Султан': [51.1694, 71.4491],
        'Актобе': [50.2839, 57.1669],
        'Уральск': [51.23, 51.37],
        'Атырау': [47.09, 51.92],
        'Актау': [43.65, 51.19],
        'Шымкент': [42.34, 69.59],
        'Караганда': [49.80, 73.10]
      }
      
      const cityName = city.name.trim()
      if (knownCities[cityName]) {
        map.setCenter(knownCities[cityName], 12)
      }
    })
  }
}

// City change handler
const onCityChange = () => {
  if (selectedCityId.value && map) {
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
