# Desktop Frontend - Quick Reference Guide

## 🚀 Quick Start

### Access the Admin Panel
1. Navigate to: `http://localhost:5173/login`
2. Login with admin credentials (role: `superadmin` or `org_admin`)
3. Auto-redirect to: `/admin/organization/settings`

### Development Server
```bash
cd frontend
npm run dev
```

## 📍 Routes Quick Reference

| Path | Component | Description |
|------|-----------|-------------|
| `/admin/organization/settings` | OrganizationSettings | iiko credentials & org info |
| `/admin/organization/terminals` | TerminalsManagement | Terminals sync from iiko |
| `/admin/organization/payment-types` | PaymentTypesManagement | Payment types sync |
| `/admin/organization/menu` | MenuManagement | Two-step menu loading |
| `/admin/orders` | OrdersManagement | Orders table with modal |
| `/admin/users` | UsersManagement | Users & addresses |
| `/admin/products` | ProductsManagement | Products catalog |
| `/admin/modifiers` | ModifiersManagement | Modifiers table |

## 🎨 Component Props & Methods

### DesktopLayout.vue
```javascript
// No props - self-contained layout
// Methods:
toggleSidebar()    // Toggle sidebar collapse
handleLogout()     // Logout and redirect
```

### OrganizationSettings.vue
```javascript
// Uses: organizationStore
// Methods:
loadOrganization()    // Fetch org data
handleSubmit()        // Save org settings
```

### TerminalsManagement.vue
```javascript
// Uses: organizationStore.terminals
// Methods:
loadTerminals()           // Fetch terminals
handleLoadFromIiko()      // Sync from iiko
```

### PaymentTypesManagement.vue
```javascript
// Uses: organizationStore.paymentTypes
// Methods:
loadPaymentTypes()        // Fetch payment types
handleLoadFromIiko()      // Sync from iiko
```

### MenuManagement.vue
```javascript
// Uses: organizationStore.externalMenus
// Data:
selectedMenuId: ref(null)
step: ref(0)  // 1 or 2

// Methods:
handleFetchExternalMenus()  // Step 1
handleLoadMenu()            // Step 2
```

### OrdersManagement.vue
```javascript
// Uses: ordersStore.orders
// Data:
selectedOrder: ref(null)
refreshingOrderId: ref(null)

// Methods:
loadOrders()              // Fetch orders
handleViewOrder(order)    // Open modal
handleRefreshStatus(order) // Refresh from iiko
formatDate(date)
formatTime(date)
formatPrice(price)
getStatusLabel(status)
getStatusClass(status)
```

### ProductsManagement.vue
```javascript
// Uses: productsStore.products
// Data:
searchQuery: ref('')
categoryFilter: ref('')
availabilityFilter: ref('')

// Computed:
categories
filteredProducts

// Methods:
loadProducts()
formatPrice(price)
```

### ModifiersManagement.vue
```javascript
// Direct API call to /api/modifiers/
// Data:
modifiers: ref([])
searchQuery: ref('')

// Computed:
filteredModifiers

// Methods:
loadModifiers()
formatPrice(price)
```

## 🔧 Store Methods

### organizationStore
```javascript
// Getters
hasOrganization
hasIikoCredentials

// Actions
await fetchOrganization()
await updateOrganization({ iiko_organization_id, api_key, name, phone, address })
await fetchTerminals()
await loadTerminalsFromIiko()
await fetchPaymentTypes()
await loadPaymentTypesFromIiko()
await fetchExternalMenus()
await loadMenuFromIiko(menuId)
clearError()
```

### authStore (existing)
```javascript
// Getters
isAuthenticated
isSuperAdmin
isOrgAdmin
isCustomer

// Actions
await loginWithPassword(username, password)
await fetchCurrentUser()
logout()
```

### productsStore (existing)
```javascript
// State
products: []

// Actions
await fetchProducts()
```

### ordersStore (existing)
```javascript
// State
orders: []

// Actions
await fetchOrders()
```

## 🎯 Common Patterns

### API Call Pattern
```javascript
const handleAction = async () => {
  loading.value = true
  error.value = null
  successMessage.value = ''

  try {
    const result = await store.someAction()
    successMessage.value = 'Success message'
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = store.error || 'Error message'
  } finally {
    loading.value = false
  }
}
```

### Modal Pattern
```vue
<!-- Modal with Teleport -->
<Teleport to="body">
  <div v-if="showModal" class="fixed inset-0 z-50 overflow-y-auto" @click.self="showModal = false">
    <div class="flex min-h-screen items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/50"></div>
      
      <!-- Modal Content -->
      <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full">
        <!-- Content here -->
      </div>
    </div>
  </div>
</Teleport>
```

### Table Pattern
```vue
<table class="w-full">
  <thead class="bg-gray-50 dark:bg-gray-700">
    <tr>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
        Column Name
      </th>
    </tr>
  </thead>
  <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
    <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
      <td class="px-6 py-4 whitespace-nowrap">
        {{ item.name }}
      </td>
    </tr>
  </tbody>
</table>
```

### Icon Button Pattern
```vue
<button class="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
  <Icon icon="mdi:eye" class="w-5 h-5" />
</button>
```

## 🎨 Tailwind Classes Reference

### Common Colors
```
Primary (Blue):   bg-blue-600, text-blue-600, hover:bg-blue-700
Success (Green):  bg-green-600, text-green-600
Warning (Yellow): bg-yellow-600, text-yellow-600
Error (Red):      bg-red-600, text-red-600
Gray:             bg-gray-50, bg-gray-100, bg-gray-200, etc.
```

### Dark Mode
All components support dark mode with `dark:` prefix:
```
bg-white dark:bg-gray-800
text-gray-900 dark:text-white
border-gray-200 dark:border-gray-700
```

### Status Badges
```vue
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
  Active
</span>
```

### Form Inputs
```vue
<input class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
              bg-white dark:bg-gray-700 text-gray-900 dark:text-white
              focus:ring-2 focus:ring-blue-500 focus:border-transparent">
```

## 🔍 Debugging Tips

### Check Authentication
```javascript
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()

console.log('Is authenticated:', authStore.isAuthenticated)
console.log('Is admin:', authStore.isSuperAdmin || authStore.isOrgAdmin)
console.log('User:', authStore.user)
```

### Check API Calls
```javascript
// In browser console
localStorage.getItem('access_token')  // Check if token exists
```

### Check Store State
```javascript
import { useOrganizationStore } from '@/stores/organization'
const orgStore = useOrganizationStore()

console.log('Organization:', orgStore.organization)
console.log('Loading:', orgStore.loading)
console.log('Error:', orgStore.error)
```

## 📦 Expected Backend Response Formats

### Organization
```json
{
  "id": 1,
  "iiko_organization_id": "uuid-here",
  "api_key": "key-here",
  "name": "My Organization",
  "phone": "+7 (XXX) XXX-XX-XX",
  "address": "Street address"
}
```

### Terminals
```json
[
  {
    "id": 1,
    "iiko_terminal_id": "uuid-here",
    "name": "Terminal 1",
    "is_active": true
  }
]
```

### Payment Types
```json
[
  {
    "id": 1,
    "iiko_payment_id": "uuid-here",
    "name": "Наличные",
    "payment_type": "CASH",
    "is_active": true
  }
]
```

### External Menus
```json
[
  {
    "id": "uuid-here",
    "external_menu_id": "uuid-here",
    "name": "Main Menu"
  }
]
```

### Orders
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "user1",
      "first_name": "John",
      "phone": "+7..."
    },
    "items": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "name": "Pizza"
        },
        "quantity": 2,
        "price": 1500
      }
    ],
    "delivery_address": {
      "city_name": "Almaty",
      "street_name": "Abay",
      "house": "10",
      "flat": "5"
    },
    "total_price": 3000,
    "status": "pending",
    "created_at": "2024-01-14T12:00:00Z"
  }
]
```

## 🛠️ Troubleshooting

### Issue: Components not rendering
- Check if routes are properly configured in `router/index.js`
- Verify `DesktopLayout.vue` is imported correctly
- Check browser console for errors

### Issue: API calls failing
- Verify backend is running
- Check CORS settings
- Inspect Network tab in DevTools
- Verify API endpoints match backend routes

### Issue: Icons not showing
- Ensure `@iconify/vue` is installed: `npm install @iconify/vue`
- Check icon names at https://icon-sets.iconify.design/
- Verify Icon component is imported: `import { Icon } from '@iconify/vue'`

### Issue: Dark mode not working
- Check if Tailwind config includes dark mode
- Verify `dark:` classes are applied
- Check HTML class toggling for dark mode

### Issue: Sidebar not collapsing
- Check `sidebarOpen` ref state
- Verify transition classes are applied
- Inspect with Vue DevTools

## 📚 Resources

- [Iconify Icon Sets](https://icon-sets.iconify.design/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Pinia State Management](https://pinia.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)

---

**Quick Command Reference:**
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```
