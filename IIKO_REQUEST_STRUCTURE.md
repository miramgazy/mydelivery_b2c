# Структура запроса, отправляемого в iiko API

## Endpoint
```
POST https://api-ru.iiko.services/api/1/deliveries/create
```

## Структура JSON запроса

### Базовая структура (заказ без модификаторов)

```json
{
  "organizationId": "uuid-организации",
  "terminalGroupId": "uuid-терминала",
  "order": {
    "orderServiceType": "DeliveryByCourier",
    "status": "Unconfirmed",
    "customer": {
      "name": "Имя клиента",
      "phone": "+77771234567"
    },
    "phone": "+77771234567",
    "deliveryPoint": {
      "address": {
        "city": "Алматы",
        "street": {
          "id": "uuid-улицы"
        },
        "house": "1",
        "flat": "10",
        "entrance": "1",
        "floor": "2",
        "comment": "Комментарий к адресу"
      }
    },
    "items": [
      {
        "type": "Product",
        "productId": "uuid-продукта",
        "amount": 2.0,
        "price": 1500.0
      }
    ],
    "customerPayments": [
      {
        "paymentTypeId": "uuid-типа-оплаты",
        "sum": 3000.0
      }
    ],
    "comment": "Комментарий к заказу"
  }
}
```

### Заказ с модификаторами

```json
{
  "organizationId": "uuid-организации",
  "terminalGroupId": "uuid-терминала",
  "order": {
    "orderServiceType": "DeliveryByCourier",
    "status": "Unconfirmed",
    "customer": {
      "name": "Имя клиента",
      "phone": "+77771234567"
    },
    "phone": "+77771234567",
    "deliveryPoint": {
      "address": {
        "city": "Алматы",
        "street": {
          "id": "uuid-улицы"
        },
        "house": "1"
      }
    },
    "items": [
      {
        "type": "Product",
        "productId": "uuid-продукта-пицца",
        "amount": 2.0,
        "price": 1500.0,
        "modifiers": [
          {
            "productId": "uuid-модификатора-сыр",
            "amount": 3.0
          },
          {
            "productId": "uuid-модификатора-грибы",
            "amount": 1.0
          }
        ]
      }
    ],
    "customerPayments": [
      {
        "paymentTypeId": "uuid-типа-оплаты",
        "sum": 4200.0
      }
    ]
  }
}
```

### Заказ с координатами (без адреса)

```json
{
  "organizationId": "uuid-организации",
  "terminalGroupId": "uuid-терминала",
  "order": {
    "orderServiceType": "DeliveryByCourier",
    "status": "Unconfirmed",
    "customer": {
      "name": "Имя клиента",
      "phone": "+77771234567"
    },
    "phone": "+77771234567",
    "deliveryPoint": {
      "type": "coordinates",
      "coordinates": {
        "latitude": 43.2220,
        "longitude": 76.8512
      },
      "address": {
        "city": "Алматы"
      }
    },
    "items": [
      {
        "type": "Product",
        "productId": "uuid-продукта",
        "amount": 1.0,
        "price": 1500.0
      }
    ]
  }
}
```

## Важные моменты

### Модификаторы
- `modifiers` - массив объектов, каждый содержит:
  - `productId` - UUID продукта-модификатора из iiko (берется из `Modifier.modifier_code`)
  - `amount` - количество модификатора (float)
- Модификаторы добавляются только если они есть у позиции заказа
- `productId` модификатора должен быть валидным UUID продукта из iiko

### Типы данных
- Все UUID конвертируются в строки: `str(uuid)`
- Количества и суммы конвертируются в float: `float(value)`
- Телефон нормализуется: `+77771234567` (только цифры с префиксом `+`)

### Обязательные поля
- `organizationId` - ID организации в iiko
- `terminalGroupId` - ID группы терминалов
- `order.orderServiceType` - тип сервиса (всегда `DeliveryByCourier`)
- `order.status` - статус (всегда `Unconfirmed`)
- `order.customer.name` - имя клиента
- `order.phone` - телефон клиента
- `order.deliveryPoint` - точка доставки (адрес или координаты)
- `order.items` - массив позиций заказа

### Опциональные поля
- `order.customerPayments` - добавляется только если `payment_type.is_active == True`
- `order.comment` - комментарий к заказу
- `deliveryPoint.address.flat`, `entrance`, `floor`, `comment` - дополнительные поля адреса

## Логирование

В коде добавлено детальное логирование:
1. Базовая информация о заказе (количество позиций, IDs)
2. Детали модификаторов для каждой позиции
3. **Полный JSON запрос** (в логах уровня INFO)

Для просмотра полного запроса проверьте логи при отправке заказа.
