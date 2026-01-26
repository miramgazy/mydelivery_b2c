# 🔌 Доступ к базе данных PostgreSQL

## Открытые порты для внешнего подключения

### docker-compose.b2c.yml
- **Порт**: `5436:5432`
- **Подключение**: `localhost:5436`
- **Параметры по умолчанию**:
  - Database: `mydelivery_b2c`
  - User: `postgres`
  - Password: из переменной `DB_PASSWORD` в `.env.b2c`

### backend/docker-compose.yml (Development)
- **Порт**: `5432:5432`
- **Подключение**: `localhost:5432`
- **Параметры по умолчанию**:
  - Database: `iiko_delivery`
  - User: `postgres`
  - Password: из переменной `DB_PASSWORD` в `.env`

### backend/docker-compose.prod.yml (Production)
- **Порт**: `5432:5432`
- **Подключение**: `localhost:5432`
- **Параметры по умолчанию**:
  - Database: `iiko_delivery`
  - User: `postgres`
  - Password: из переменной `DB_PASSWORD` в `.env`

### docker-compose.yml
- **База данных**: Внешняя (управляется через Coolify network)
- **Подключение**: Через `DATABASE_URL` переменную окружения

### docker-compose.coolify.yml
- **База данных**: Внешняя (управляется Coolify)
- **Подключение**: Через `DATABASE_URL` переменную окружения

## Примеры подключения

### Через psql (командная строка)
```bash
# Для B2C
psql -h localhost -p 5436 -U postgres -d mydelivery_b2c

# Для Development
psql -h localhost -p 5432 -U postgres -d iiko_delivery
```

### Через DBeaver / pgAdmin / другие клиенты
```
Host: localhost
Port: 5436 (для B2C) или 5432 (для Development/Production)
Database: mydelivery_b2c (для B2C) или iiko_delivery (для других)
Username: postgres
Password: [из .env файла]
```

### Через Python
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5436,  # или 5432 для других конфигураций
    database="mydelivery_b2c",
    user="postgres",
    password="your_password"
)
```

### Connection String
```
postgresql://postgres:password@localhost:5436/mydelivery_b2c
```

## Безопасность

⚠️ **Важно**: 
- Порты открыты на `0.0.0.0`, что означает доступ извне
- Для production рекомендуется:
  1. Использовать firewall для ограничения доступа
  2. Изменить пароль по умолчанию
  3. Использовать SSL соединения
  4. Ограничить доступ только с определенных IP адресов

## Проверка доступности

```bash
# Проверка подключения
nc -zv localhost 5436  # для B2C
nc -zv localhost 5432  # для Development/Production

# Или через psql
psql -h localhost -p 5436 -U postgres -d mydelivery_b2c -c "SELECT version();"
```
