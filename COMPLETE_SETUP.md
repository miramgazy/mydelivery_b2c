# 🚀 Полная инструкция по запуску проекта

## Архитектура

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80)                │
│         Reverse Proxy + Static              │
└────┬─────────────────┬──────────────────────┘
     │                 │
     ↓                 ↓
┌─────────┐      ┌────────────┐
│ Vue     │      │ Django     │
│Frontend │      │ Backend    │
│Port 5173│      │ Port 8000  │
└─────────┘      └─────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   ┌────────┐    ┌─────────┐   ┌─────────┐
   │Postgres│    │  Redis  │   │ Celery  │
   └────────┘    └─────────┘   └─────────┘
```

## Быстрый старт (5 минут)

### 1. Клонирование

```bash
git clone <repository-url>
cd iiko_delivery_system
```

### 2. Настройка Backend

```bash
# Создать .env для backend
cp .env.example .env

# Отредактировать (обязательно!)
nano .env
```

Минимальные настройки:
```env
SECRET_KEY=<сгенерируйте новый>
TELEGRAM_BOT_TOKEN=<от BotFather>
TELEGRAM_BOT_USERNAME=<имя бота>
DB_PASSWORD=<надежный пароль>
```

### 3. Настройка Frontend

```bash
# Создать структуру frontend
mkdir -p frontend/src/{components,views,stores,services,router,utils,composables,assets}

# Создать .env для frontend
cp frontend/.env.example frontend/.env

# Отредактировать
nano frontend/.env
```

```env
VITE_API_URL=http://localhost/api
```

### 4. Запуск через Nginx

```bash
# Запустить все сервисы
make init

# Или вручную:
docker-compose build
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### 5. Проверка

```bash
# Проверить что все работает
curl http://localhost/health  # → "healthy"
curl http://localhost/api/    # → API root

# Открыть в браузере:
# - http://localhost/ → Vue Frontend
# - http://localhost/admin/ → Django Admin
# - http://localhost/api/schema/swagger-ui/ → API Docs
```

## Структура проекта

```
iiko_delivery_system/
├── backend/                    # Django backend
│   ├── apps/
│   │   ├── users/
│   │   ├── organizations/
│   │   ├── products/
│   │   └── orders/
│   ├── config/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Vue frontend
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── services/
│   │   └── router/
│   ├── Dockerfile
│   └── package.json
│
├── nginx.conf                  # Nginx config (dev)
├── nginx.prod.conf             # Nginx config (prod)
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
└── Makefile                    # Команды управления
```

## Endpoints и порты

### Development

| Сервис | URL | Порт | Описание |
|--------|-----|------|----------|
| Nginx | http://localhost/ | 80 | Главный вход |
| Frontend | http://localhost:5173 | 5173 | Vue dev server (напрямую) |
| Backend | http://localhost:8000 | 8000 | Django (напрямую) |
| PostgreSQL | localhost:5432 | 5432 | БД (напрямую) |
| Redis | localhost:6379 | 6379 | Redis (напрямую) |

### Через Nginx (рекомендуется)

| Путь | Куда идет | Описание |
|------|-----------|----------|
| http://localhost/ | Frontend | Vue приложение |
| http://localhost/api/ | Backend | REST API |
| http://localhost/admin/ | Backend | Django Admin |
| http://localhost/static/ | Nginx | Статика Django |
| http://localhost/media/ | Nginx | Медиа файлы |

## Workflow разработки

### Backend разработка

```bash
# 1. Создать новое приложение
docker-compose exec backend python manage.py startapp myapp

# 2. Создать миграции
make makemigrations

# 3. Применить миграции
make migrate

# 4. Django shell
make shell

# 5. Тесты
make test

# 6. Логи
make logs-backend
```

### Frontend разработка

```bash
# 1. Зайти в контейнер
docker-compose exec frontend sh

# 2. Установить новый пакет
npm install package-name

# 3. Сборка
npm run build

# 4. Логи
make logs-frontend

# 5. Перезапуск с HMR
# Изменения подхватываются автоматически
```

### Nginx

```bash
# Проверить конфигурацию
docker-compose exec nginx nginx -t

# Перезагрузить без даунтайма
docker-compose exec nginx nginx -s reload

# Логи
make logs-nginx

# Проверить доступность
curl -I http://localhost/
```

## B2B Workflow

### 1. Создание организации (Суперадмин)

```bash
make shell
```

```python
from apps.users.models import Role
from apps.organizations.models import Organization, Terminal, PaymentType

# Создать терминал
terminal = Terminal.objects.create(
    terminal_group_id='your-iiko-terminal-uuid',
    terminal_group_name='Главный терминал'
)

# Создать организацию
org = Organization.objects.create(
    org_name='ТОО "Моя компания"',
    api_key='your-iiko-api-key',
    city='Актобе',
    terminal_group=terminal
)

# Создать тип оплаты
payment = PaymentType.objects.create(
    payment_id='iiko-payment-uuid',
    payment_name='Безналичный',
    payment_type='Card',
    organization=org
)

print(f"Организация: {org.org_name}")
print(f"ID: {org.org_id}")
```

### 2. Создание администратора организации

```python
from apps.users.models import User, Role

admin_role = Role.objects.get(role_name='org_admin')

admin = User.objects.create(
    telegram_id=YOUR_TELEGRAM_ID,
    first_name='Администратор',
    role=admin_role,
    organization=org
)

print(f"Админ создан: {admin.full_name}")
print(f"Telegram ID: {admin.telegram_id}")
```

### 3. Массовое создание сотрудников (через API)

```bash
# Получить JWT токен админа
TOKEN=$(curl -X POST http://localhost/api/auth/telegram/ \
  -H "Content-Type: application/json" \
  -d '{"initData": "..."}' \
  | jq -r '.access')

# Создать список сотрудников
curl -X POST http://localhost/api/users/bulk_create/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_ids": [111222333, 444555666, 777888999],
    "organization_id": "org-uuid-from-step-1",
    "role": "customer"
  }'
```

### 4. Сотрудники заходят в Mini App

1. Открывают бота в Telegram
2. Нажимают кнопку запуска Mini App
3. Проверка доступа → Вход → Меню

## Production деплой

### 1. Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Установить Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Настройка домена

```bash
# В DNS добавить A записи:
# @ → IP сервера
# www → IP сервера
```

### 3. Настройка переменных

```bash
# Скопировать и настроить .env
cp .env.example .env
nano .env
```

Production настройки:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=<очень-сильный-ключ>
DB_PASSWORD=<очень-сильный-пароль>

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. SSL сертификат

```bash
# Получить сертификат
make ssl-init

# Ввести домен и email
```

### 5. Запуск production

```bash
# Сборка
make prod-build

# Запуск
make prod-up

# Миграции
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Статика
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Создать суперюзера
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 6. Проверка

```bash
# Логи
make prod-logs

# Health check
curl https://your-domain.com/health

# Тест SSL
curl -I https://your-domain.com/
```

## Мониторинг

### Логи

```bash
# Все сервисы
make logs

# Конкретный сервис
make logs-backend
make logs-frontend
make logs-nginx

# Последние 100 строк
docker-compose logs --tail=100 backend

# Follow mode
docker-compose logs -f backend
```

### Метрики

```bash
# Использование ресурсов
docker stats

# Статус контейнеров
docker-compose ps

# Дисковое пространство
df -h
docker system df
```

### Health Checks

```bash
# Nginx
curl http://localhost/health

# Backend API
curl http://localhost/api/

# PostgreSQL
docker-compose exec db pg_isready -U postgres

# Redis
docker-compose exec redis redis-cli ping
```

## Бэкапы

### База данных

```bash
# Создать бэкап
docker-compose exec -T db pg_dump -U postgres iiko_delivery | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Восстановить
gunzip < backup_20240115_120000.sql.gz | docker-compose exec -T db psql -U postgres iiko_delivery

# Автоматический бэкап (cron)
0 2 * * * cd /path/to/project && make backup
```

### Медиа файлы

```bash
# Бэкап медиа
tar -czf media_backup_$(date +%Y%m%d).tar.gz -C . media/

# Восстановить
tar -xzf media_backup_20240115.tar.gz
```

## Troubleshooting

### Nginx 502 Bad Gateway

```bash
# Проверить backend
docker-compose ps backend
make logs-backend

# Перезапустить
docker-compose restart backend
```

### Frontend не загружается

```bash
# Проверить сборку
docker-compose exec frontend npm run build

# Проверить nginx конфиг
docker-compose exec nginx nginx -t

# Перезагрузить nginx
docker-compose exec nginx nginx -s reload
```

### Медленная работа

```bash
# Проверить ресурсы
docker stats

# Проверить логи медленных запросов
make logs-backend | grep "Slow query"

# Добавить индексы в БД
make shell
# Анализ запросов Django ORM
```

## Useful Commands

```bash
# Полная очистка и перезапуск
make clean-all
make init

# Обновление кода
git pull
docker-compose build
docker-compose up -d
make migrate

# Проверка безопасности
docker-compose exec backend python manage.py check --deploy

# Размер БД
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('iiko_delivery'));"

# Количество пользователей
docker-compose exec backend python manage.py shell -c "from apps.users.models import User; print(User.objects.count())"
```

## Поддержка

- 📖 [README.md](README.md) - Основная документация
- 🏢 [B2B_SETUP.md](B2B_SETUP.md) - B2B настройка
- 🐳 [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker
- 🌐 [NGINX_SETUP.md](NGINX_SETUP.md) - Nginx
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура