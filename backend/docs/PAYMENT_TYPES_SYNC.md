# Загрузка типов оплаты из iiko Cloud

## Описание
Функционал позволяет загружать список типов оплаты из iiko Cloud в базу данных приложения через админ-панель Django.

## Как использовать

### Через админ-панель Django

1. Войдите в админ-панель Django
2. Перейдите в раздел **Организации** → **Типы оплаты**
3. Нажмите кнопку **"Загрузить типы оплаты из iiko"** в правом верхнем углу
4. Выберите организацию из выпадающего списка
5. Нажмите **"Загрузить типы оплаты"**

### Что происходит при загрузке

1. Система подключается к iiko Cloud API используя API ключ организации
2. Запрашивает список типов оплаты через endpoint `/api/1/payment_types`
3. Синхронизирует данные с локальной базой данных:
   - Создает новые типы оплаты
   - Обновляет существующие
   - Пропускает удаленные типы оплаты (где `isDeleted: true`)

### Требования

- Организация должна иметь:
  - Заполненное поле **API Key iiko**
  - Заполненное поле **ID организации в iiko**
- Организация должна быть активна (`is_active = True`)

### Структура данных

Каждый тип оплаты содержит:
- `payment_id` - UUID из iiko (первичный ключ)
- `payment_name` - Название типа оплаты
- `payment_type` - Код типа оплаты (например, "External", "Cash", "Card")
- `organization` - Связь с организацией
- `is_active` - Флаг активности

## Технические детали

### Файлы

1. **Backend:**
   - `apps/iiko_integration/client.py` - метод `get_payment_types()`
   - `apps/iiko_integration/services.py` - метод `sync_payment_types()`
   - `apps/organizations/admin.py` - `PaymentTypeAdmin` с кастомными методами
   - `apps/organizations/models.py` - модель `PaymentType`

2. **Templates:**
   - `apps/organizations/templates/admin/organizations/paymenttype_changelist.html` - список с кнопкой
   - `apps/organizations/templates/admin/organizations/sync_payment_types.html` - форма выбора организации

### API Endpoint

```
POST https://api-ru.iiko.services/api/1/payment_types
```

**Request:**
```json
{
  "organizationIds": ["<uuid>"]
}
```

**Response:**
```json
{
  "paymentTypes": [
    {
      "id": "<uuid>",
      "name": "Наличные",
      "paymentTypeKind": "Cash",
      "isDeleted": false
    }
  ]
}
```

## Примечания

- При повторной загрузке существующие типы оплаты будут обновлены
- Типы оплаты с флагом `isDeleted: true` будут пропущены
- Если `payment_id` уже существует в базе, запись будет обновлена и переназначена текущей организации
