#!/bin/bash

set -e

echo "=== Coolify Deployment Entrypoint ==="

# Coolify использует DATABASE_URL, парсим его если нужно
if [ -n "$DATABASE_URL" ]; then
    echo "Using DATABASE_URL from Coolify"
    # DATABASE_URL уже настроен, используем его напрямую
else
    echo "WARNING: DATABASE_URL not set, trying to parse from individual variables"
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ] && [ -n "$DB_NAME" ] && [ -n "$DB_USER" ] && [ -n "$DB_PASSWORD" ]; then
        export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    fi
fi

# Ожидание базы данных (для Coolify БД может быть внешней)
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
    max_attempts=60
    attempt=0
    while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
        attempt=$((attempt + 1))
        if [ $attempt -ge $max_attempts ]; then
            echo "ERROR: PostgreSQL is not available after $max_attempts attempts"
            exit 1
        fi
        echo "PostgreSQL is unavailable - waiting... ($attempt/$max_attempts)"
        sleep 1
    done
    echo "PostgreSQL connection available"
else
    echo "DB_HOST/DB_PORT not set, assuming external database managed by Coolify"
    # Даем время на подключение к внешней БД
    sleep 5
fi

# Проверка подключения к БД через Django
echo "Verifying database connection..."
python << EOF
import sys
import time
import os
import django
from django.core.management import execute_from_command_line

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("Database connection verified successfully")
        sys.exit(0)
    except OperationalError as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f"ERROR: Failed to connect to database after {max_retries} attempts: {e}")
            sys.exit(1)
        print(f"Database connection failed, retrying... ({retry_count}/{max_retries})")
        time.sleep(2)
EOF

# Миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Сбор статики (с оптимизацией для маломощных серверов)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 0 || echo "WARNING: collectstatic failed, continuing..."

# Инициализация ролей
echo "Creating initial roles if not exist..."
python manage.py shell -c "
from apps.users.models import Role
roles = [
    ('superadmin', 'Суперадминистратор системы'),
    ('org_admin', 'Администратор организации'),
    ('customer', 'Клиент'),
]
for role_name, description in roles:
    Role.objects.get_or_create(
        role_name=role_name,
        defaults={'description': description}
    )
print('Roles initialized')
" || echo "WARNING: Role initialization failed, continuing..."

echo "=== Entrypoint completed, starting server ==="
exec "$@"
