#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
# Увеличиваем интервал ожидания для более надежной проверки
max_attempts=60
attempt=0
while ! nc -z $DB_HOST $DB_PORT; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "ERROR: PostgreSQL is not available after $max_attempts attempts"
    exit 1
  fi
  echo "PostgreSQL is unavailable - waiting... ($attempt/$max_attempts)"
  sleep 1
done
echo "PostgreSQL started"

# Дополнительная проверка: убеждаемся, что БД действительно готова принимать подключения
echo "Verifying PostgreSQL connection..."
python << EOF
import sys
import time
import psycopg2
from psycopg2 import OperationalError

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host="${DB_HOST}",
            port="${DB_PORT}",
            database="${DB_NAME}",
            user="${DB_USER}",
            password="${DB_PASSWORD}"
        )
        conn.close()
        print("PostgreSQL connection verified successfully")
        sys.exit(0)
    except OperationalError as e:
        retry_count += 1
        if retry_count >= max_retries:
            print(f"ERROR: Failed to connect to PostgreSQL after {max_retries} attempts: {e}")
            sys.exit(1)
        print(f"PostgreSQL connection failed, retrying... ({retry_count}/{max_retries})")
        time.sleep(1)
EOF

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

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
"

echo "Starting server..."
exec "$@"