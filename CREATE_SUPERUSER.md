# 👤 Создание суперпользователя Django

## Способ 1: Через Docker exec (рекомендуется для Coolify)

### Шаг 1: Найдите имя контейнера backend

```bash
docker ps | grep backend
```

Вы увидите что-то вроде:
```
7f064a374e81   w88c4ogc88gk00w8sog08skk-backend   ...   backend-w88c4ogc88gk00w8sog08skk-134042200204
```

### Шаг 2: Выполните команду создания суперпользователя

```bash
docker exec -it backend-w88c4ogc88gk00w8sog08skk-134042200204 python manage.py createsuperuser
```

**Замените `backend-w88c4ogc88gk00w8sog08skk-134042200204` на реальное имя вашего контейнера!**

### Шаг 3: Введите данные суперпользователя

Вам будет предложено ввести:
- **Username** (имя пользователя)
- **Email address** (email адрес) - опционально
- **Password** (пароль) - дважды для подтверждения

Пример:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

## Способ 2: Через Docker Compose (если доступен)

Если у вас есть доступ к `docker-compose` в директории проекта:

```bash
cd /path/to/project
docker-compose -f docker-compose.coolify.yml exec backend python manage.py createsuperuser
```

## Способ 3: Неинтерактивный способ (через shell)

Если нужно создать суперпользователя без интерактивного ввода:

```bash
docker exec -it backend-w88c4ogc88gk00w8sog08skk-134042200204 python manage.py shell
```

Затем в Python shell:

```python
from apps.users.models import User

User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='your_secure_password_here'
)
```

Или если у вас кастомная модель User:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='your_secure_password_here'
)
```

## Доступ к админ-панели

После создания суперпользователя вы можете войти в Django Admin:

- **URL**: `https://b2c-delivery.mevent.kz/admin/`
- **Или через API**: `https://b2c-delivery.mevent.kz/api/admin/`

## Проверка создания

Проверить, что суперпользователь создан:

```bash
docker exec -it backend-w88c4ogc88gk00w8sog08skk-134042200204 python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    print(f"Username: {user.username}, Email: {user.email}, Is Superuser: {user.is_superuser}")
```

## Устранение проблем

### Ошибка: "container not found"
- Убедитесь, что контейнер запущен: `docker ps`
- Используйте правильное имя контейнера

### Ошибка: "database connection failed"
- Проверьте, что база данных запущена и здорова: `docker ps | grep db`
- Проверьте переменные окружения в Coolify

### Ошибка: "migrations not applied"
- Примените миграции: `docker exec -it backend-w88c4ogc88gk00w8sog08skk-134042200204 python manage.py migrate`
