# 🐳 Запуск проекта в Docker

## Быстрый старт (3 команды)

```bash
# 1. Создать .env файл
cp .env.example .env

# 2. Отредактировать .env (укажите TELEGRAM_BOT_TOKEN и SECRET_KEY)
nano .env  # или vim, или любой редактор

# 3. Запустить проект
make init
```

Готово! Проект запущен на http://localhost:8000

---

## Подробная инструкция

### 1. Предварительные требования

Убедитесь что установлены:
- Docker (версия 20.10+)
- Docker Compose (версия 2.0+)
- Make (опционально, для удобства)

Проверка версий:
```bash
docker --version
docker-compose --version
make --version
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Откройте `.env` и настройте:

**Обязательные параметры:**
```env
SECRET_KEY=your-very-secret-key-here-generate-new-one
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=your_bot_name
```

Сгенерировать SECRET_KEY:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Опциональные параметры:**
```env
DEBUG=True  # Установите False для production
DB_PASSWORD=change_this_password  # Измените для безопасности
```

### 3. Запуск проекта

#### Вариант A: С использованием Make (рекомендуется)

```bash
# Полная инициализация проекта
make init

# Это выполнит:
# - Сборку Docker образов
# - Запуск всех контейнеров
# - Применение миграций
# - Создание суперпользователя
```

#### Вариант B: Вручную через docker-compose

```bash
# Сборка образов
docker-compose build

# Запуск контейнеров
docker-compose up -d

# Применение миграций
docker-compose exec backend python manage.py migrate

# Создание суперпользователя
docker-compose exec backend python manage.py createsuperuser
```

### 4. Проверка работы

```bash
# Проверить статус всех контейнеров
docker-compose ps

# Должны быть запущены:
# - iiko_delivery_db (PostgreSQL)
# - iiko_delivery_redis (Redis)
# - iiko_delivery_backend (Django)
# - iiko_delivery_celery (Celery Worker)
# - iiko_delivery_celery_beat (Celery Beat)
```

Все контейнеры должны быть в статусе "Up" или "Up (healthy)".

### 5. Доступ к сервисам

После запуска доступны:

| Сервис | URL | Описание |
|--------|-----|----------|
| API | http://localhost:8000/api/ | REST API |
| Swagger | http://localhost:8000/api/schema/swagger-ui/ | Интерактивная документация API |
| ReDoc | http://localhost:8000/api/schema/redoc/ | Альтернативная документация |
| Admin | http://localhost:8000/admin/ | Django Admin панель |
| PostgreSQL | localhost:5432 | База данных (для внешних клиентов) |

### 6. Создание тестовых данных

```bash
# Открыть Django shell
make shell

# Или
docker-compose exec backend python manage.py shell
```

В shell создайте тестовую организацию и пользователей:

```python
from apps.users.models import User, Role
from apps.organizations.models import Organization, Terminal

# Создать терминал
terminal = Terminal.objects.create(
    terminal_group_id='your-terminal-uuid',
    terminal_group_name='Главный терминал'
)

# Создать организацию
org = Organization.objects.create(
    org_name='Тестовый ресторан',
    api_key='your-iiko-api-key',
    city='Актобе',
    terminal_group=terminal
)

# Создать роль админа организации
admin_role = Role.objects.get(role_name='org_admin')

# Создать пользователя админа
admin_user = User.objects.create(
    telegram_id=123456789,
    first_name='Админ',
    role=admin_role,
    organization=org
)

print(f"Создана организация: {org.org_name}")
print(f"Создан пользователь: {admin_user.full_name}")
```

---

## 🔧 Полезные команды

### Управление контейнерами

```bash
# Просмотр логов
make logs              # Все сервисы
make logs-backend      # Только backend
make logs-celery       # Только celery

# Перезапуск
make restart           # Перезапустить все
docker-compose restart backend  # Только backend

# Остановка
make down              # Остановить все

# Запуск
make up                # Запустить все
```

### Работа с Django

```bash
# Миграции
make migrate           # Применить
make makemigrations    # Создать

# Shell
make shell            # Django shell
make bash             # Bash в контейнере

# Статика
make collectstatic    # Собрать статические файлы

# Тесты
make test             # Запустить тесты
```

### Работа с базой данных

```bash
# Подключиться к PostgreSQL
docker-compose exec db psql -U postgres -d iiko_delivery

# Создать бэкап
docker-compose exec db pg_dump -U postgres iiko_delivery > backup.sql

# Восстановить из бэкапа
docker-compose exec -T db psql -U postgres iiko_delivery < backup.sql

# Очистить базу (ОСТОРОЖНО!)
make clean-all  # Удалит все данные
```

### Отладка

```bash
# Просмотреть переменные окружения в контейнере
docker-compose exec backend env

# Выполнить произвольную команду
docker-compose exec backend python manage.py your_command

# Проверить подключение к БД
docker-compose exec backend python manage.py dbshell

# Проверить установленные пакеты
docker-compose exec backend pip list
```

---

## 🚀 Production развертывание

### 1. Настройка для production

В `.env` установите:

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=very-strong-secret-key-for-production
DB_PASSWORD=strong-database-password

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Использование Nginx (рекомендуется)

Раскомментируйте секцию nginx в `docker-compose.yml` и создайте `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 3. SSL сертификаты

Используйте Let's Encrypt с Certbot:

```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx

# Получите сертификат
sudo certbot --nginx -d your-domain.com
```

### 4. Мониторинг

Добавьте мониторинг:
- Sentry для отслеживания ошибок
- Prometheus + Grafana для метрик
- ELK Stack для логов

---

## ❗ Troubleshooting

### Проблема: Контейнер backend не запускается

```bash
# Проверьте логи
docker-compose logs backend

# Частые причины:
# 1. Неправильные переменные в .env
# 2. База данных не готова - подождите несколько секунд и перезапустите
docker-compose restart backend
```

### Проблема: Ошибка подключения к БД

```bash
# Убедитесь что PostgreSQL запущен
docker-compose ps db

# Проверьте логи БД
docker-compose logs db

# Перезапустите БД
docker-compose restart db
```

### Проблема: Миграции не применяются

```bash
# Удалите все и пересоздайте
make clean-all
make init
```

### Проблема: Порт уже занят

Если порт 8000 занят, измените в `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Используйте другой порт
```

---

## 📚 Дополнительные ресурсы

- [Docker документация](https://docs.docker.com/)
- [Docker Compose документация](https://docs.docker.com/compose/)
- [Django документация](https://docs.djangoproject.com/)
- [DRF документация](https://www.django-rest-framework.org/)

---

## 📝 Checklist перед деплоем

- [ ] `DEBUG=False` в production
- [ ] Сильный `SECRET_KEY`
- [ ] Надежный пароль БД
- [ ] Настроен HTTPS
- [ ] Настроены CORS для фронтенда
- [ ] Созданы бэкапы БД
- [ ] Настроен мониторинг
- [ ] Настроены логи
- [ ] Проверены миграции
- [ ] Проверены статические файлы