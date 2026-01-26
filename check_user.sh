#!/bin/bash
# Скрипт для проверки и исправления суперпользователя

echo "=== Проверка суперпользователя ==="

# Найдите имя контейнера backend
BACKEND_CONTAINER=$(docker ps | grep backend | awk '{print $NF}')

if [ -z "$BACKEND_CONTAINER" ]; then
    echo "Ошибка: контейнер backend не найден"
    exit 1
fi

echo "Используется контейнер: $BACKEND_CONTAINER"

# Проверка существующих суперпользователей
echo ""
echo "=== Список суперпользователей ==="
docker exec -it $BACKEND_CONTAINER python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print(f"Has Password: {bool(user.password)}")
        print("---")
else:
    print("Суперпользователи не найдены")
EOF

echo ""
echo "=== Проверка пользователя по email ==="
docker exec -it $BACKEND_CONTAINER python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

email = "miramgazy@gmail.com"
user = User.objects.filter(email=email).first()

if user:
    print(f"Найден пользователь:")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is Active: {user.is_active}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    print(f"Has Password: {bool(user.password)}")
else:
    print(f"Пользователь с email {email} не найден")
EOF
