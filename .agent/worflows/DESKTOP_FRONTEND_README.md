# Desktop Frontend Implementation

## Overview
This document describes the desktop admin panel implementation for the iiko delivery system. The desktop interface is fully responsive and does not interfere with the existing Telegram Mini App functionality.

## Architecture

### Layout System
- **DesktopLayout.vue**: Main layout component for desktop admin panel
  - Collapsible sidebar with smooth animations
  - 4 main sections: Organization, Orders, Clients, Products
  - Responsive design using Tailwind CSS
  - Dark mode support

### Routes Structure

```
/admin (DesktopLayout)
├── /organization/settings - Organization settings
├── /organization/terminals - Terminals management
├── /organization/payment-types - Payment types management
├── /organization/menu - Menu sync from iiko
├── /orders - Orders management
├── /users - Users and clients management
├── /products - Products management
└── /modifiers - Modifiers management
```

## Components & Views

### Organization Section

#### 1. Organization Settings (`OrganizationSettings.vue`)
- **Purpose**: Configure iiko integration credentials
- **Fields**:
  - `iiko_organization_id`: Organization UUID in iiko
  - `api_key`: iiko Cloud API key (password masked)
  - `name`: Organization name
  - `phone`: Contact phone
  - `address`: Organization address
- **Features**:
  - Form validation
  - Success/error notifications
  - Auto-save with loading states

#### 2. Terminals Management (`TerminalsManagement.vue`)
- **Purpose**: Manage payment terminals from iiko
- **Features**:
  - Table view of all terminals
  - "Load from iiko" button to sync terminals
  - Display terminal name, iiko ID, and status
  - Empty state with helpful message

#### 3. Payment Types Management (`PaymentTypesManagement.vue`)
- **Purpose**: Manage payment types from iiko
- **Features**:
  - Table view of all payment types
  - "Load from iiko" button to sync payment types
  - Display payment name, type, and status
  - Type labels (CASH, CARD, ONLINE, etc.)

#### 4. Menu Management (`MenuManagement.vue`)
- **Purpose**: Two-step menu synchronization from iiko
- **Workflow**:
  1. **Step 1**: Fetch available external menus from iiko
  2. **Step 2**: Select specific menu and load it
- **Features**:
  - Visual menu selection with radio buttons
  - Loading states for each step
  - Success/error notifications

### Orders Section

#### Orders Management (`OrdersManagement.vue`)
- **Purpose**: Comprehensive order management
- **Features**:
  - Full-width table with order details
  - Order information: ID, client, date, amount, status
  - **Actions** (Iconify icons):
    - `mdi:eye` - View order details in modal
    - `mdi:refresh` - Refresh order status from iiko
  - **Modal View**: Displays complete order details
    - Client information
    - Delivery address
    - Order items table with quantities and prices
    - Total calculation
- **Status Colors**: Visual status indicators (pending, confirmed, preparing, ready, delivered, cancelled)

### Clients Section

#### Users Management (`UsersManagement.vue`)
- **Purpose**: Manage users and their delivery addresses
- **Features**:
  - User listing with profiles
  - Delivery addresses management
  - Modal-based editing
  - One user → Multiple addresses relationship

### Products Section

#### 1. Products Management (`ProductsManagement.vue`)
- **Purpose**: Manage product catalog
- **Features**:
  - **Filters**:
    - Search by name
    - Category filter
    - Availability filter
  - **Table Columns**:
    - Product photo
    - Name and description
    - Category
    - Price
    - Modifiers indicator
    - Availability status
  - Responsive design with image placeholders

#### 2. Modifiers Management (`ModifiersManagement.vue`)
- **Purpose**: Manage product modifiers
- **Features**:
  - Search functionality
  - Table view showing:
    - Modifier name and description
    - Associated product
    - Price (with "free" indicator)
    - Availability status

## Services & State Management

### API Services

#### `organization.service.js`
```javascript
- getOrganization()
- updateOrganization(data)
- getTerminals()
- loadTerminalsFromIiko()
- getPaymentTypes()
- loadPaymentTypesFromIiko()
- getExternalMenus()
- loadMenuFromIiko(menuId)
```

### Pinia Stores

#### `organization.js` Store
- **State**: organization, terminals, paymentTypes, externalMenus, loading, error
- **Getters**: hasOrganization, hasIikoCredentials
- **Actions**: All organization-related operations

#### Existing Stores (Reused)
- `auth.js` - Authentication and user management
- `products.js` - Products catalog
- `orders.js` - Orders management
- `cart.js` - Shopping cart (TMA)

## Technical Requirements

### Icons
- **Library**: @iconify/vue (already installed)
- **Usage**: All buttons use semantic icons
- **Examples**:
  - `mdi:eye` - View/Preview
  - `mdi:refresh` - Reload/Sync
  - `mdi:download` - Download/Load
  - `mdi:cog` - Settings
  - `mdi:food` - Menu/Products

### Responsive Design
- **Tailwind CSS**: All components use Tailwind utilities
- **Mobile First**: TMA routes remain unchanged
- **Desktop Breakpoint**: `lg:` and above for desktop layout
- **Dark Mode**: Full dark mode support with `dark:` classes

### Security
- **Authentication**: Login/password required for desktop access
- **Route Guards**: All admin routes protected by `requiresAdmin` meta
- **Role Check**: Both `superadmin` and `org_admin` have access
- **Auto-redirect**: Unauthorized users redirected to home

## API Endpoints Expected

The frontend expects these backend endpoints:

```
GET    /api/organizations/me/
PATCH  /api/organizations/me/
GET    /api/organizations/terminals/
POST   /api/organizations/load-terminals/
GET    /api/organizations/payment-types/
POST   /api/organizations/load-payment-types/
GET    /api/organizations/external-menus/
POST   /api/organizations/load-menu/
GET    /api/modifiers/
```

## Development Workflow

### Testing Locally
1. Start development server:
   ```bash
   npm run dev
   ```

2. Login with admin credentials at `/login`

3. Access admin panel at `/admin`

### Building for Production
```bash
npm run build
```

## File Structure

```
frontend/src/
├── layouts/
│   └── DesktopLayout.vue          # Main desktop layout
├── views/admin/
│   ├── OrganizationSettings.vue   # Organization settings
│   ├── TerminalsManagement.vue    # Terminals
│   ├── PaymentTypesManagement.vue # Payment types
│   ├── MenuManagement.vue         # Menu sync
│   ├── OrdersManagement.vue       # Orders table & modal
│   ├── UsersManagement.vue        # Users & addresses
│   ├── ProductsManagement.vue     # Products catalog
│   └── ModifiersManagement.vue    # Modifiers
├── services/
│   ├── api.js                     # Base API client
│   ├── organization.service.js    # Organization API
│   └── ...
├── stores/
│   ├── auth.js                    # Auth store
│   ├── organization.js            # Organization store
│   ├── products.js                # Products store
│   └── orders.js                  # Orders store
└── router/
    └── index.js                   # Routes configuration
```

## Features Summary

✅ **Adaptive Design**: Desktop and mobile (TMA) work independently
✅ **Collapsible Sidebar**: Smooth animations with transition-all
✅ **4 Main Sections**: Organization, Orders, Clients, Products
✅ **Organization Management**: Settings, terminals, payment types, menu sync
✅ **Orders Table**: Full-featured with modal view and iiko sync
✅ **Clients Management**: Users and addresses
✅ **Products Catalog**: Filtering and search
✅ **Modifiers Table**: Associated products display
✅ **Icon-only Buttons**: Semantic Iconify icons throughout
✅ **State Management**: Pinia stores for all data
✅ **Security**: Protected routes with role-based access
✅ **Dark Mode**: Complete dark mode support

## Next Steps

1. **Backend Integration**: Ensure all API endpoints are implemented
2. **Testing**: Test all admin operations with real iiko credentials
3. **Optimization**: Add pagination for large tables
4. **Enhanced Features**:
   - Bulk operations for products
   - Advanced order filtering
   - Export functionality
   - Real-time updates via WebSocket
