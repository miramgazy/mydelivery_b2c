# API Request/Response Examples

## 🔗 Complete API Integration Examples

### 1. Organization Management

#### GET /api/organizations/me/
**Получить данные текущей организации**

**Request:**
```http
GET /api/organizations/me/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "org_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "My Restaurant",
  "org_name": "My Restaurant",
  "iiko_organization_id": "cafe4567-e89b-12d3-a456-426614174abc",
  "api_key": "********************************",
  "phone": "+7 (777) 123-45-67",
  "address": "г. Алматы, ул. Абая, д. 10",
  "city": "Алматы",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-14T12:00:00Z",
  "terminals": []
}
```

---

#### PATCH /api/organizations/me/
**Обновить настройки организации**

**Request:**
```http
PATCH /api/organizations/me/
Authorization: Bearer <token>
Content-Type: application/json

{
  "iiko_organization_id": "cafe4567-e89b-12d3-a456-426614174abc",
  "api_key": "your-iiko-api-key-here",
  "name": "Updated Restaurant Name",
  "phone": "+7 (777) 999-88-77",
  "address": "г. Алматы, ул. Достык, д. 5"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Restaurant Name",
  "org_name": "Updated Restaurant Name",
  "iiko_organization_id": "cafe4567-e89b-12d3-a456-426614174abc",
  "api_key": "your-iiko-api-key-here",
  "phone": "+7 (777) 999-88-77",
  "address": "г. Алматы, ул. Достык, д. 5",
  "is_active": true,
  "updated_at": "2024-01-14T13:00:00Z"
}
```

---

### 2. Terminals Management

#### GET /api/organizations/terminals/
**Получить список терминалов**

**Request:**
```http
GET /api/organizations/terminals/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "term1234-e89b-12d3-a456-426614174000",
    "terminal_id": "term1234-e89b-12d3-a456-426614174000",
    "iiko_terminal_id": "term1234-e89b-12d3-a456-426614174000",
    "name": "Terminal Group 1",
    "terminal_group_name": "Terminal Group 1",
    "iiko_organization_id": "cafe4567-e89b-12d3-a456-426614174abc",
    "is_active": true,
    "organization": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2024-01-10T10:00:00Z",
    "updated_at": "2024-01-10T10:00:00Z"
  },
  {
    "id": "term5678-e89b-12d3-a456-426614174001",
    "terminal_id": "term5678-e89b-12d3-a456-426614174001",
    "iiko_terminal_id": "term5678-e89b-12d3-a456-426614174001",
    "name": "Terminal Group 2",
    "terminal_group_name": "Terminal Group 2",
    "is_active": false,
    "organization": "123e4567-e89b-12d3-a456-426614174000"
  }
]
```

---

#### POST /api/organizations/load-terminals/
**Загрузить терминалы из iiko**

**Request:**
```http
POST /api/organizations/load-terminals/
Authorization: Bearer <token>
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "message": "Терминалы успешно загружены из iiko",
  "success": true
}
```

**Response (400 BAD REQUEST):**
```json
{
  "error": "Не настроены iiko_organization_id или api_key"
}
```

---

### 3. Payment Types Management

#### GET /api/organizations/payment-types/
**Получить список типов оплат**

**Request:**
```http
GET /api/organizations/payment-types/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "pay1234-e89b-12d3-a456-426614174000",
    "payment_id": "pay1234-e89b-12d3-a456-426614174000",
    "iiko_payment_id": "pay1234-e89b-12d3-a456-426614174000",
    "name": "Наличные",
    "payment_name": "Наличные",
    "payment_type": "CASH",
    "organization": "123e4567-e89b-12d3-a456-426614174000",
    "is_active": true,
    "created_at": "2024-01-10T11:00:00Z",
    "updated_at": "2024-01-10T11:00:00Z"
  },
  {
    "id": "pay5678-e89b-12d3-a456-426614174001",
    "payment_id": "pay5678-e89b-12d3-a456-426614174001",
    "iiko_payment_id": "pay5678-e89b-12d3-a456-426614174001",
    "name": "Банковская карта",
    "payment_name": "Банковская карта",
    "payment_type": "CARD",
    "organization": "123e4567-e89b-12d3-a456-426614174000",
    "is_active": true
  }
]
```

---

#### POST /api/organizations/load-payment-types/
**Загрузить типы оплат из iiko**

**Request:**
```http
POST /api/organizations/load-payment-types/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Типы оплат успешно загружены из iiko",
  "success": true
}
```

---

### 4. Menu Management (Two-Step Process)

#### Step 1: GET /api/organizations/external-menus/
**Получить список доступных меню**

**Request:**
```http
GET /api/organizations/external-menus/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "menu1234-e89b-12d3-a456-426614174000",
    "external_menu_id": "menu1234-e89b-12d3-a456-426614174000",
    "name": "Основное меню"
  },
  {
    "id": "menu5678-e89b-12d3-a456-426614174001",
    "external_menu_id": "menu5678-e89b-12d3-a456-426614174001",
    "name": "Летнее меню"
  }
]
```

---

#### Step 2: POST /api/organizations/load-menu/
**Загрузить выбранное меню**

**Request:**
```http
POST /api/organizations/load-menu/
Authorization: Bearer <token>
Content-Type: application/json

{
  "external_menu_id": "menu1234-e89b-12d3-a456-426614174000"
}
```

**Response (200 OK):**
```json
{
  "message": "Меню успешно загружено из iiko",
  "success": true
}
```

**Response (400 BAD REQUEST):**
```json
{
  "error": "Не указан external_menu_id"
}
```

---

### 5. Products Management

#### GET /api/products/
**Получить список продуктов**

**Request:**
```http
GET /api/products/?organization=123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "prod1234-e89b-12d3-a456-426614174000",
    "product_id": "prod1234-e89b-12d3-a456-426614174000",
    "name": "Маргарита",
    "product_name": "Маргарита",
    "price": "1500.00",
    "description": "Классическая пицца с томатами и моцареллой",
    "image_url": "https://example.com/images/margarita.jpg",
    "category": {
      "subgroup_id": "cat1234-e89b-12d3-a456-426614174000",
      "subgroup_name": "Пиццы",
      "order_index": 1
    },
    "is_available": true,
    "has_modifiers": true,
    "order_index": 1
  },
  {
    "id": "prod5678-e89b-12d3-a456-426614174001",
    "product_id": "prod5678-e89b-12d3-a456-426614174001",
    "name": "Пепперони",
    "product_name": "Пепперони",
    "price": "1800.00",
    "description": "Пицца с острой пепперони",
    "image_url": null,
    "category": {
      "subgroup_id": "cat1234-e89b-12d3-a456-426614174000",
      "subgroup_name": "Пиццы",
      "order_index": 1
    },
    "is_available": true,
    "has_modifiers": false,
    "order_index": 2
  }
]
```

**Query Parameters:**
- `organization` - UUID организации
- `category` - UUID категории
- `is_available` - true/false
- `search` - Поиск по названию или описанию

---

### 6. Modifiers Management

#### GET /api/modifiers/
**Получить список модификаторов**

**Request:**
```http
GET /api/modifiers/?product=prod1234-e89b-12d3-a456-426614174000
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "mod1234-e89b-12d3-a456-426614174000",
    "modifier_id": "mod1234-e89b-12d3-a456-426614174000",
    "name": "Дополнительный сыр",
    "modifier_name": "Дополнительный сыр",
    "description": "От 1 до 3",
    "product": "prod1234-e89b-12d3-a456-426614174000",
    "product_name": "Маргарита",
    "price": "200.00",
    "min_amount": 1,
    "max_amount": 3,
    "modifier_weight": null,
    "is_required": false,
    "is_available": true
  },
  {
    "id": "mod5678-e89b-12d3-a456-426614174001",
    "modifier_id": "mod5678-e89b-12d3-a456-426614174001",
    "name": "Соус барбекю",
    "modifier_name": "Соус барбекю",
    "description": "От 1 до 2 | Обязательно",
    "product": "prod1234-e89b-12d3-a456-426614174000",
    "product_name": "Маргарита",
    "price": "0.00",
    "min_amount": 1,
    "max_amount": 2,
    "is_required": true,
    "is_available": true
  }
]
```

**Query Parameters:**
- `product` - UUID продукта

---

### 7. Orders Management

#### GET /api/orders/
**Получить список заказов**

**Request:**
```http
GET /api/orders/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": {
      "id": 100,
      "username": "user123",
      "first_name": "Иван",
      "phone": "+7 (777) 111-22-33"
    },
    "items": [
      {
        "id": 1,
        "product": {
          "id": "prod1234-e89b-12d3-a456-426614174000",
          "name": "Маргарита"
        },
        "quantity": 2,
        "price": "1500.00"
      }
    ],
    "delivery_address": {
      "city_name": "Алматы",
      "street_name": "Абая",
      "house": "10",
      "flat": "5"
    },
    "total_price": "3000.00",
    "status": "pending",
    "created_at": "2024-01-14T10:00:00Z",
    "updated_at": "2024-01-14T10:00:00Z"
  }
]
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "error": "Не указан external_menu_id"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "error": "Организация не найдена"
}
```

### 500 Internal Server Error
```json
{
  "error": "Неожиданная ошибка: <error details>"
}
```

---

## 🔐 Authentication Header

All requests require authentication token:

```http
Authorization: Bearer <your-access-token>
```

Get token from:
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

Response:
```json
{
  "access": "<access-token>",
  "refresh": "<refresh-token>"
}
```

---

## 📋 Frontend Usage Examples

### Organization Store

```javascript
import { useOrganizationStore } from '@/stores/organization'

const orgStore = useOrganizationStore()

// Fetch organization
await orgStore.fetchOrganization()

// Update organization
await orgStore.updateOrganization({
  iiko_organization_id: 'uuid-here',
  api_key: 'key-here',
  name: 'My Restaurant',
  phone: '+7 (777) 123-45-67',
  address: 'Some address'
})

// Load terminals from iiko
await orgStore.loadTerminalsFromIiko()

// Load payment types
await orgStore.loadPaymentTypesFromIiko()

// Get external menus
await orgStore.fetchExternalMenus()

// Load specific menu
await orgStore.loadMenuFromIiko(menuId)
```

---

**Last Updated:** 2026-01-14  
**API Version:** v1  
**Base URL:** `http://localhost:8000/api` (development)
