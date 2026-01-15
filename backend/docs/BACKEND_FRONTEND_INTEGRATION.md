# Backend-Frontend Integration Guide

## Обзор

Этот документ описывает полную интеграцию между бэкендом Django и фронтендом Vue 3, реализованную для tg-delivery проекта.

## 🔗 API Endpoints

### Organizations API

#### Base URL: `/api/organizations/`

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/me/` | GET | Получить организацию текущего пользователя | - | OrganizationSerializer |
| `/me/` | PATCH | Обновить организацию | OrganizationData | OrganizationSerializer |
| `/terminals/` | GET | Получить терминалы организации | - | TerminalSerializer[] |
| `/load-terminals/` | POST | Загрузить терминалы из iiko | - | {message, success} |
| `/payment-types/` | GET | Получить типы оплат | - | PaymentTypeSerializer[] |
| `/load-payment-types/` | POST | Загрузить типы оплат из iiko | - | {message, success} |
| `/external-menus/` | GET | Получить список внешних меню | - | ExternalMenuSerializer[] |
| `/load-menu/` | POST | Загрузить меню из iiko | {external_menu_id} | {message, success} |

### Products API

#### Base URL: `/api/products/`

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Получить список продуктов | ProductListSerializer[] |
| `/{id}/` | GET | Получить детали продукта | ProductDetailSerializer |

### Modifiers API

#### Base URL: `/api/modifiers/`

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Получить список модификаторов | ModifierSerializer[] |
| `/{id}/` | GET | Получить детали модификатора | ModifierSerializer |

### Orders API

#### Base URL: `/api/orders/`

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Получить список заказов | OrderListSerializer[] |
| `/{id}/` | GET | Получить детали заказа | OrderDetailSerializer |
| `/my_orders/` | GET | Заказы текущего пользователя | OrderListSerializer[] |
| `/{id}/cancel/` | POST | Отменить заказ | OrderDetailSerializer |
| `/{id}/status/` | GET | Обновить статус из iiko | OrderDetailSerializer |

### Users API

#### Base URL: `/api/users/`

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Список пользователей | UserSerializer[] |
| `/me/` | GET | Текущий пользователь | UserSerializer |
| `/{id}/` | GET | Детали пользователя | UserSerializer |

---

## 📊 Data Models

### User Model

```python
{
    "id": integer,
    "full_name": "string",
    "phone": "string",
    "role_name": "string",     # CUSTOMER, ORG_ADMIN, SUPER_ADMIN
    "organization_name": "string",
    "addresses": DeliveryAddress[]
}
```

### Order Model

```python
{
    "id": "uuid",              # order_id
    "order_id": "uuid",        # Primary key
    "order_number": "string",
    "user_name": "string",
    "organization_name": "string",
    "status": "string",        # pending, confirmed, ...
    "status_display": "string", # Human readable
    "total_amount": decimal,
    "total_price": decimal,    # Alias for frontend
    "items_count": integer,
    "created_at": "datetime"
}
```

### Organization Model

```python
{
    "id": "uuid",               # org_id
    "org_id": "uuid",          # Primary key
    "name": "string",          # org_name mapping
    "org_name": "string",      # Original field
    "iiko_organization_id": "string",
    "api_key": "string",
    "phone": "string",         # NEW FIELD
    "address": "string",       # NEW FIELD
    "city": "string",
    "is_active": boolean,
    "created_at": "datetime",
    "updated_at": "datetime",
    "terminals": Terminal[]    # Related
}
```

### Terminal Model

```python
{
    "id": "uuid",                    # terminal_id
    "terminal_id": "uuid",           # Primary key
    "iiko_terminal_id": "uuid",      # Alias for terminal_id
    "name": "string",                # terminal_group_name mapping
    "terminal_group_name": "string", # Original field
    "iiko_organization_id": "string",
    "is_active": boolean,
    "organization": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Payment Type Model

```python
{
    "id": "uuid",              # payment_id
    "payment_id": "uuid",      # Primary key
    "iiko_payment_id": "uuid", # Alias for payment_id
    "name": "string",          # payment_name mapping
    "payment_name": "string",  # Original field
    "payment_type": "string",  # CASH, CARD, ONLINE, etc.
    "organization": "uuid",
    "is_active": boolean,
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Product Model

```python
{
    "id": "uuid",           # product_id
    "product_id": "uuid",   # Primary key
    "name": "string",       # product_name mapping
    "product_name": "string",
    "price": decimal,
    "description": "string",
    "image_url": "string",
    "category": {
        "subgroup_id": "uuid",
        "subgroup_name": "string",
        "order_index": integer
    },
    "is_available": boolean,
    "has_modifiers": boolean,
    "order_index": integer,
    "organization": "uuid"
}
```

### Modifier Model

```python
{
    "id": "uuid",          # modifier_id
    "modifier_id": "uuid", # Primary key
    "name": "string",      # modifier_name mapping
    "modifier_name": "string",
    "description": "string", # Generated field
    "product": "uuid",
    "product_name": "string", # From related product
    "price": decimal,
    "min_amount": integer,
    "max_amount": integer,
    "is_required": boolean,
    "is_available": boolean
}
```

---

## 🔄 Integration Flow

### 1. Organization Setup Flow

```
Frontend: /admin/organization/settings
    ↓
User enters: iiko_organization_id, api_key, name, phone, address
    ↓
PATCH /api/organizations/me/
    ↓
Backend: OrganizationViewSet.update_current_organization()
    ↓
Update Organization model
    ↓
Return updated organization
```

### 2. Terminals Sync Flow

```
Frontend: /admin/organization/terminals
    ↓
User clicks "Загрузить из IIKO"
    ↓
POST /api/organizations/load-terminals/
    ↓
Backend: OrganizationViewSet.load_terminals()
    ↓
IikoClient.get_terminal_groups()
    ↓
MenuSyncService.sync_terminal_groups()
    ↓
Save terminals to Database
    ↓
Return success message
```

### 3. Payment Types Sync Flow

```
Frontend: /admin/organization/payment-types
    ↓
User clicks "Загрузить из IIKO"
    ↓
POST /api/organizations/load-payment-types/
    ↓
Backend: OrganizationViewSet.load_payment_types()
    ↓
IikoClient.get_payment_types()
    ↓
MenuSyncService.sync_payment_types()
    ↓
Save payment types to Database
    ↓
Return success message
```

### 4. Menu Sync Flow (Two-Step)

#### Step 1: Get External Menus List

```
Frontend: /admin/organization/menu
    ↓
User clicks "Выгрузить меню из IIKO"
    ↓
GET /api/organizations/external-menus/
    ↓
Backend: OrganizationViewSet.get_external_menus()
    ↓
IikoClient.get_external_menus()
    ↓
Parse and format menu list
    ↓
Return ExternalMenuSerializer[]
```

#### Step 2: Load Specific Menu

```
Frontend: User selects menu
    ↓
User clicks "Загрузить выбранное меню"
    ↓
POST /api/organizations/load-menu/
Body: { external_menu_id: "uuid" }
    ↓
Backend: OrganizationViewSet.load_menu()
    ↓ IikoClient.get_menu()
    ↓
MenuSyncService.sync_menu()
    ↓
Save Menu, Categories, Products, Modifiers
    ↓
Return success message
```

---

## 🛠️ Backend Changes Made

### 1. Models

#### organizations/models.py
- ✅ Added `phone` field to Organization
- ✅ Added `address` field to Organization

### 2. Serializers

#### organizations/serializers.py
- ✅ Updated OrganizationSerializer with field mappings
  - `id` → `org_id`
  - `name` → `org_name`
  - Added `phone` and `address`
- ✅ Updated TerminalSerializer with field mappings
  - `id`, `name`, `iiko_terminal_id`
- ✅ Updated PaymentTypeSerializer with field mappings
  - `id`, `name`, `iiko_payment_id`
- ✅ Added ExternalMenuSerializer

#### products/serializers.py
- ✅ Enhanced ModifierSerializer
  - Added `id`, `name`, `description`, `product_name`, `is_available`
  - Added `get_description()` method
- ✅ Enhanced ProductListSerializer
  - Added `id`, `name` mappings
  - Changed category to nested object
- ✅ Enhanced ProductDetailSerializer
  - Added `id`, `name` mappings
  - Changed category to nested object

### 3. Views

#### organizations/views.py
- ✅ Created custom actions in OrganizationViewSet:
  - `@action get_current_organization()` - GET /me/
  - `@action update_current_organization()` - PATCH /me/
  - `@action get_terminals()` - GET /terminals/
  - `@action load_terminals()` - POST /load-terminals/
  - `@action get_payment_types()` - GET /payment-types/
  - `@action load_payment_types()` - POST /load-payment-types/
  - `@action get_external_menus()` - GET /external-menus/
  - `@action load_menu()` - POST /load-menu/

### 4. Migrations

#### organizations/migrations/0007_organization_address_organization_phone.py
- ✅ Created and applied migration for new fields

---

## 🎯 Frontend Services Configuration

### organizationService API Methods

```javascript
// GET /api/organizations/me/
getOrganization()

// PATCH /api/organizations/me/
updateOrganization(data)

// GET /api/organizations/terminals/
getTerminals()

// POST /api/organizations/load-terminals/
loadTerminalsFromIiko()

// GET /api/organizations/payment-types/
getPaymentTypes()

// POST /api/organizations/load-payment-types/
loadPaymentTypesFromIiko()

// GET /api/organizations/external-menus/
getExternalMenus()

// POST /api/organizations/load-menu/
loadMenuFromIiko(menuId)
```

---

## ✅ Testing Checklist

### Organization Endpoints

- [ ] GET `/api/organizations/me/` returns current organization
- [ ] PATCH `/api/organizations/me/` updates organization
- [ ] Phone and address fields saved correctly
- [ ] API key displayed but can be updated

### Terminals Endpoints

- [ ] GET `/api/organizations/terminals/` returns list
- [ ] POST `/api/organizations/load-terminals/` syncs from iiko
- [ ] Terminals display with correct names and statuses

### Payment Types Endpoints

- [ ] GET `/api/organizations/payment-types/` returns list
- [ ] POST `/api/organizations/load-payment-types/` syncs from iiko
- [ ] Payment types show correct types (CASH, CARD, etc.)

### Menu Endpoints

- [ ] GET `/api/organizations/external-menus/` returns menu list
- [ ] POST `/api/organizations/load-menu/` loads specific menu
- [ ] Products synced with categories
- [ ] Modifiers synced with products

### Products Endpoints

- [ ] GET `/api/products/` returns products list
- [ ] Products have nested category objects
- [ ] `has_modifiers` flag is accurate

### Modifiers Endpoints

- [ ] GET `/api/modifiers/` returns modifiers list
- [ ] Modifiers include product_name
- [ ] Description field generated correctly

---

## 🔐 Authentication & Permissions

### Required for All Endpoints
- User must be authenticated (Bearer token)
- Token sent in Authorization header

### Permission Levels
1. **Customer** (`is_customer`)
   - Can view products and orders
   - Cannot access admin endpoints

2. **Organization Admin** (`is_org_admin`)
   - Can access /admin/* routes
   - Can manage organization settings
   - Can sync data from iiko

3. **Super Admin** (`is_superadmin`)
   - Full access to all endpoints
   - Can manage multiple organizations

### Organization Logic
- If user has `organization` field → use that organization
- Otherwise → use first active organization
- Frontend should handle organization assignment

---

## 🐛 Common Issues & Solutions

### Issue 1: "Организация не найдена"
**Cause:** User not linked to organization  
**Solution:** 
1. Check user.organization field in database
2. Ensure at least one active organization exists
3. Update user model to include organization reference

### Issue 2: "Не настроены iiko_organization_id или api_key"
**Cause:** Organization credentials not set  
**Solution:**
1. Navigate to Organization Settings
2. Fill in iiko_organization_id and api_key
3. Save settings

### Issue 3: Terminals/Payment Types not loading
**Cause:** iiko API error or invalid credentials  
**Solution:**
1. Verify iiko credentials are correct
2. Check backend logs for iiko API errors
3. Ensure iiko_organization_id matches organization in iiko

### Issue 4: Menu not syncing
**Cause:** External menu ID invalid or sync error  
**Solution:**
1. Try fetching external menus list again
2. Check if menu exists in iiko
3. Review backend logs for sync errors

---

## 📝 Environment Variables

### Backend (.env)
```bash
# Required for iiko Integration
IIKO_API_URL=https://api-ru.iiko.services/api/1
IIKO_API_URL_V2=https://api-ru.iiko.services/api/2

# Database
DATABASE_URL=postgresql://user:pass@db:5432/dbname

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_TELEGRAM_BOT_TOKEN=your-bot-token
```

---

## 🚀 Deployment Steps

### Backend
1. Apply migrations:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

2. Collect static files:
   ```bash
   docker-compose exec backend python manage.py collectstatic --noinput
   ```

3. Restart services:
   ```bash
   docker-compose restart backend
   ```

### Frontend
1. Build for production:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy build files to server

---

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [iiko Cloud API Documentation](https://api-ru.iiko.services/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Pinia State Management](https://pinia.vuejs.org/)

---

**Last Updated:** 2026-01-14  
**Integration Status:** ✅ Complete  
**Backend Version:** Django 4.x + DRF  
**Frontend Version:** Vue 3 + Vite
