#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

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