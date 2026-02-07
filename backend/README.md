# iiko Delivery System - Telegram Mini App

Система заказов через Telegram Mini App с интеграцией iiko для доставки еды.

## Архитектура

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Vue 3 (отдельный репозиторий)
- **Database**: PostgreSQL
- **Message Broker**: Redis + Celery
- **Integration**: iiko API

## Основные возможности

### Для клиентов (через Telegram Mini App)
- Просмотр меню с категориями и продуктами
- Добавление товаров в корзину с модификаторами
- Оформление заказа с выбором адреса доставки
- Отслеживание статуса заказа

### Для администраторов
- Управление организациями
- Управление пользователями и ролями
- Синхронизация меню с iiko
- Мониторинг заказов
- Логирование действий

## Установка и запуск

### Требования

- Docker 20.10+
- Docker Compose 2.0+

### Быстрый старт с Docker

#### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd iiko_delivery_system
```

#### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и настройте переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл и укажите:
- `SECRET_KEY` - секретный ключ Django (сгенерируйте новый)
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `TELEGRAM_BOT_USERNAME` - username вашего бота

```env
SECRET_KEY=your-generated-secret-key-here
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_bot
```

#### 3. Запуск всех сервисов

```bash
# Сборка и запуск в фоновом режиме
docker-compose up -d --build

# Или для просмотра логов
docker-compose up --build
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Django Backend (порт 8000)
- Celery Worker
- Celery Beat

#### 4. Проверка статуса

```bash
# Проверить статус контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f backend

# Логи конкретного сервиса
docker-compose logs -f celery
```

#### 5. Создание суперпользователя

```bash
docker-compose exec backend python manage.py createsuperuser
```

#### 6. Доступ к приложению

- API: http://localhost:8000/api/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/
- Django Admin: http://localhost:8000/administrator/ (офис фронта — /admin)

### Управление контейнерами

```bash
# Остановка всех сервисов
docker-compose stop

# Запуск остановленных сервисов
docker-compose start

# Перезапуск
docker-compose restart

# Полная остановка и удаление контейнеров
docker-compose down

# Остановка с удалением volumes (УДАЛИТ ВСЕ ДАННЫЕ!)
docker-compose down -v

# Пересборка после изменений в коде
docker-compose up -d --build
```

### Работа с базой данных

```bash
# Применить миграции
docker-compose exec backend python manage.py migrate

# Создать миграции
docker-compose exec backend python manage.py makemigrations

# Доступ к PostgreSQL
docker-compose exec db psql -U postgres -d iiko_delivery

# Выполнить SQL скрипт
docker-compose exec db psql -U postgres -d iiko_delivery -f /docker-entrypoint-initdb.d/your_script.sql
```

### Django команды

```bash
# Выполнить любую Django команду
docker-compose exec backend python manage.py <command>

# Примеры:
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py createsuperuser
```

### Разработка с Docker

Для разработки можно настроить hot-reload:

```bash
# В docker-compose.yml замените команду backend на:
command: python manage.py runserver 0.0.0.0:8000
```

Изменения в коде будут автоматически подхватываться.

---

## Установка и запуск БЕЗ Docker (альтернативный способ)

### Требования

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd iiko_delivery_system
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE iiko_delivery;
CREATE USER iiko_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE iiko_delivery TO iiko_user;
```

Примените SQL схему:

```bash
psql -U iiko_user -d iiko_delivery -f drawSQL-pgsql-export-improved.sql
```

### 5. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Django
SECRET_KEY=your-secret-key-here-generate-with-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=iiko_delivery
DB_USER=iiko_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_BOT_USERNAME=your_bot_username

# iiko API
IIKO_API_BASE_URL=https://api-ru.iiko.services/api/1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 6. Применение миграций Django

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

При создании потребуется указать:
- Telegram ID (можно получить через бота @userinfobot)
- Имя пользователя

### 8. Загрузка начальных данных (опционально)

```bash
python manage.py loaddata initial_roles.json
```

### 9. Запуск сервера разработки

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: `http://localhost:8000`

### 10. Запуск Celery (в отдельном терминале)

```bash
celery -A config worker -l info
```

### 11. Запуск Celery Beat для периодических задач (опционально)

```bash
celery -A config beat -l info
```

## API Документация

После запуска сервера документация API доступна по адресам:

- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## Структура API эндпоинтов

### Аутентификация
- `POST /api/auth/telegram/` - Аутентификация через Telegram initData
- `POST /api/auth/token/` - Получение JWT токена
- `POST /api/auth/token/refresh/` - Обновление JWT токена

### Пользователи
- `GET /api/users/me/` - Получение данных текущего пользователя
- `PUT /api/users/me/` - Обновление данных пользователя
- `GET /api/users/` - Список пользователей (только для админов)
- `POST /api/users/` - Создание пользователя

### Организации
- `GET /api/organizations/` - Список организаций
- `GET /api/organizations/{id}/` - Детали организации
- `POST /api/organizations/sync-menu/` - Синхронизация меню с iiko

### Продукты
- `GET /api/products/` - Список продуктов
- `GET /api/products/{id}/` - Детали продукта
- `GET /api/categories/` - Категории продуктов

### Заказы
- `POST /api/orders/` - Создание заказа
- `GET /api/orders/` - История заказов
- `GET /api/orders/{id}/` - Детали заказа
- `GET /api/orders/{id}/status/` - Статус заказа

### Адреса доставки
- `GET /api/delivery-addresses/` - Список адресов
- `POST /api/delivery-addresses/` - Добавление адреса
- `PUT /api/delivery-addresses/{id}/` - Обновление адреса
- `DELETE /api/delivery-addresses/{id}/` - Удаление адреса

## Роли пользователей

### Superadmin (Суперадминистратор)
- Полный доступ ко всем функциям системы
- Создание и управление организациями
- Создание администраторов организаций
- Просмотр всех заказов и статистики

### Org Admin (Администратор организации)
- Управление пользователями своей организации
- Управление меню и продуктами
- Просмотр заказов организации
- Синхронизация с iiko

### Customer (Клиент)
- Просмотр меню
- Создание заказов
- Просмотр своих заказов
- Управление адресами доставки

## Интеграция с Telegram Mini App

### Процесс аутентификации

1. Пользователь открывает Mini App в Telegram
2. Frontend получает `initData` от Telegram WebApp
3. Frontend отправляет `initData` на бэкенд для валидации
4. Бэкенд проверяет подпись и создает/обновляет пользователя
5. Возвращается JWT токен для дальнейших запросов

### Пример запроса аутентификации

```javascript
// Frontend (Vue)
const initData = window.Telegram.WebApp.initData;

const response = await fetch('http://localhost:8000/api/auth/telegram/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ initData })
});

const { access, refresh, user } = await response.json();
```

## Интеграция с iiko

### Синхронизация меню

```bash
python manage.py sync_menu --organization-id <uuid>
```

### Создание заказа

Система автоматически отправляет заказы в iiko при их создании.
Формат данных соответствует iiko API v1.

## Разработка

### Создание новых миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black .
flake8 .
```

## Production развертывание

### Рекомендации

1. Используйте `gunicorn` или `uvicorn` вместо `runserver`
2. Настройте HTTPS
3. Используйте PostgreSQL в production режиме
4. Настройте логирование
5. Используйте переменные окружения для секретов
6. Настройте мониторинг (Sentry, Prometheus)
7. Настройте регулярные бэкапы БД

### Пример запуска с gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Troubleshooting

### Ошибка подключения к PostgreSQL

Проверьте настройки в `.env` файле и доступность БД:

```bash
psql -U iiko_user -d iiko_delivery -h localhost
```

### Ошибка валидации Telegram initData

Убедитесь, что `TELEGRAM_BOT_TOKEN` в `.env` соответствует вашему боту.

### Ошибки iiko API

Проверьте:
- Валидность API ключа
- Доступность iiko API
- Формат отправляемых данных

## Лицензия

MIT

## Контакты

Для вопросов и поддержки: support@example.com