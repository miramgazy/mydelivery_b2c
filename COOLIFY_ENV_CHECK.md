# ✅ Проверка .env файла для Coolify

## ❌ Найденные проблемы:

### 1. **Опечатка в Redis URL**
```
❌ CELERY_BROKER_URL=redis-b2c://redis:6379/0
❌ CELERY_RESULT_BACKEND=redis-b2c://redis:6379/0
```
**Должно быть:**
```
✅ CELERY_BROKER_URL=redis://tg-redis:6379/0
✅ CELERY_RESULT_BACKEND=redis://tg-redis:6379/0
```
*Примечание: В Coolify Redis контейнер называется `tg-redis`, а не `redis`*

### 2. **Отсутствует DATABASE_URL**
Coolify обычно предоставляет `DATABASE_URL` автоматически, но если нет, entrypoint создаст его из отдельных переменных. Рекомендуется добавить явно:
```
DATABASE_URL=postgresql://postgres:yOS9IbaiSYusEmnd@db:5432/mydelivery_b2c
```

### 3. **Отсутствует REDIS_URL**
Используется в docker-compose.coolify.yml:
```
REDIS_URL=redis://tg-redis:6379/1
```

### 4. **Закомментированы важные переменные**
```
#TELEGRAM_BOT_TOKEN=7041618959:AAGREAm4n-NE1akZmznyuUSXJXVnRcuiJoA
#TELEGRAM_BOT_USERNAME=TG_MiniAppTest_Bot
```
**Нужно раскомментировать** - они используются в приложении.

### 5. **Отсутствуют SSL/Security переменные**
Для production рекомендуется добавить:
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## ✅ Исправленный .env файл:

```env
# Django Settings
SECRET_KEY=O7LKEz0BraNIq1NThB1LjPK1cZvZahtmfAqxhkUSF6zmfqEhovav3by8c2EfFEje
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend,b2c-delivery.mevent.kz

# Database (PostgreSQL)
DB_NAME=mydelivery_b2c
DB_USER=postgres
DB_PASSWORD=yOS9IbaiSYusEmnd
DB_HOST=db
DB_PORT=5432
# DATABASE_URL для Coolify (если Coolify не предоставляет автоматически)
DATABASE_URL=postgresql://postgres:yOS9IbaiSYusEmnd@db:5432/mydelivery_b2c

# Redis
REDIS_URL=redis://tg-redis:6379/1
CELERY_BROKER_URL=redis://tg-redis:6379/0
CELERY_RESULT_BACKEND=redis://tg-redis:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=7041618959:AAGREAm4n-NE1akZmznyuUSXJXVnRcuiJoA
TELEGRAM_BOT_USERNAME=TG_MiniAppTest_Bot
TELEGRAM_CONTACT_SECRET=7KoNJcQ0TBBxG5G1pgyQHuNqtztlNzh7

# iiko API
IIKO_API_BASE_URL=https://api-ru.iiko.services/api/1

# B2C Settings
ALLOW_B2C_AUTO_REGISTRATION=True
B2C_DEFAULT_ROLE=customer

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3030,http://127.0.0.1:3030,https://b2c-delivery.mevent.kz

# SSL/Security (для production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Static & Media
STATIC_URL=/static/
MEDIA_URL=/media/
```

## 📝 Примечания:

1. **DATABASE_URL**: Coolify может предоставлять эту переменную автоматически. Если она уже есть в Coolify, можно не добавлять вручную.

2. **Redis контейнер**: В `docker-compose.coolify.yml` Redis контейнер называется `tg-redis`, поэтому URL должен быть `redis://tg-redis:6379/0`, а не `redis://redis:6379/0`.

3. **TELEGRAM_BOT_TOKEN и TELEGRAM_BOT_USERNAME**: Обязательно нужны для работы Telegram Mini App. Раскомментируйте их.

4. **SSL переменные**: Для production с HTTPS обязательно установите в `True`.
