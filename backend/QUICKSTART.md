# ⚡ Быстрый старт - 5 минут

## Шаг 1: Клонирование (30 сек)

```bash
git clone <repository-url>
cd iiko_delivery_system
```

## Шаг 2: Настройка .env (2 мин)

```bash
cp .env.example .env
```

Откройте `.env` и измените минимум 2 параметра:

```env
# 1. Сгенерируйте SECRET_KEY:
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Вставьте результат:
SECRET_KEY=ваш-новый-секретный-ключ

# 2. Получите токен бота от @BotFather в Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_bot_name
```

## Шаг 3: Запуск (2 мин)

```bash
# Если установлен Make:
make init

# Или без Make:
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

При создании суперпользователя укажите:
- Telegram ID (получите от @userinfobot)
- Имя

## Шаг 4: Проверка (30 сек)

Откройте в браузере:
- ✅ http://localhost:8000/api/
- ✅ http://localhost:8000/api/schema/swagger-ui/
- ✅ http://localhost:8000/administrator/  (Django Admin; офис фронта — /admin)

## 🎉 Готово!

Бэкенд работает и готов к использованию!

---

## 🧪 Тестирование API

### 1. Получить JWT токен (для тестов без Telegram)

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_telegram_id", "password": "your_password"}'
```

### 2. Получить список продуктов

```bash
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Создать заказ

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+77779285899",
    "payment_type_id": "uuid",
    "latitude": 50.257094,
    "longitude": 57.243111,
    "items": [
      {
        "product_id": "uuid",
        "quantity": 1
      }
    ]
  }'
```

---

## 📝 Быстрая настройка тестовых данных

### Создать организацию и продукты

```bash
docker-compose exec backend python manage.py shell
```

```python
from apps.users.models import Role
from apps.organizations.models import Organization, Terminal, PaymentType
from apps.products.models import Menu, ProductCategory, Product

# Создать терминал
terminal = Terminal.objects.create(
    terminal_group_id='00000000-0000-0000-0000-000000000001',
    terminal_group_name='Тестовый терминал'
)

# Создать организацию
org = Organization.objects.create(
    org_name='Тестовый ресторан',
    api_key='test-api-key',
    city='Актобе',
    terminal_group=terminal
)

# Создать тип оплаты
payment = PaymentType.objects.create(
    payment_id='00000000-0000-0000-0000-000000000002',
    payment_name='Наличные',
    payment_type='Cash',
    organization=org
)

# Создать меню
menu = Menu.objects.create(
    menu_name='Основное меню',
    organization=org
)

# Создать категорию
category = ProductCategory.objects.create(
    subgroup_id='00000000-0000-0000-0000-000000000003',
    subgroup_name='Пицца',
    menu=menu
)

# Создать продукт
product = Product.objects.create(
    product_id='00000000-0000-0000-0000-000000000004',
    menu=menu,
    organization=org,
    product_name='Пицца Маргарита',
    price=2500,
    category=category,
    is_available=True
)

print(f"✅ Создано: {org.org_name}")
print(f"✅ Продукт: {product.product_name}")
```

---

## 🔍 Полезные команды

```bash
# Логи
make logs              # Все логи
make logs-backend      # Только backend
docker-compose logs -f # Следить за логами

# Статус
docker-compose ps      # Статус контейнеров

# Перезапуск
make restart           # Перезапустить все
docker-compose restart backend  # Только backend

# Остановка
make down              # Остановить
docker-compose stop    # Остановить без удаления

# База данных
docker-compose exec db psql -U postgres -d iiko_delivery

# Django shell
make shell
```

---

## 🐛 Если что-то не работает

### Контейнер не запускается

```bash
# Посмотреть логи ошибок
docker-compose logs backend

# Пересобрать
make clean
make build
make up
```

### Ошибка подключения к БД

```bash
# Проверить статус PostgreSQL
docker-compose ps db

# Перезапустить
docker-compose restart db
sleep 5
docker-compose restart backend
```

### Порт занят

Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Вместо 8000
```

---

## 🎯 Что дальше?

1. **Настройте iiko API**: Получите реальный API ключ
2. **Заполните БД**: Используйте n8n для синхронизации меню
3. **Создайте фронтенд**: Vue 3 приложение
4. **Настройте Telegram Bot**: Подключите Mini App

Документация:
- 📖 [README.md](README.md) - Полная документация
- 🐳 [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker инструкции
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура
- ✅ [SUMMARY.md](SUMMARY.md) - Что реализовано