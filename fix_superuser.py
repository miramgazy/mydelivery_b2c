#!/usr/bin/env python
"""
Скрипт для проверки и исправления суперпользователя
Использование: docker exec -it <container> python /app/fix_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

print("=== Проверка пользователя ===")
user = User.objects.filter(email='miramgazy@gmail.com').first()

if not user:
    print("Пользователь не найден!")
    exit(1)

print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Is Active: {user.is_active}")
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")
print(f"Password hash exists: {bool(user.password)}")
print(f"Password hash length: {len(user.password) if user.password else 0}")

# Проверка пароля
print("\n=== Тест пароля ===")
test_password = input("Введите пароль для проверки (или Enter для пропуска): ").strip()
if test_password:
    if user.check_password(test_password):
        print("✓ Пароль правильный!")
    else:
        print("✗ Пароль неправильный!")
        print("\n=== Исправление ===")
        new_password = input("Введите новый пароль: ").strip()
        if new_password:
            user.set_password(new_password)
            user.username = 'miramgazy'  # Исправляем username
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✓ Пароль обновлен и username исправлен!")
        else:
            print("Пароль не введен")
else:
    print("Проверка пароля пропущена")
    print("\n=== Создание нового суперпользователя ===")
    create_new = input("Создать нового суперпользователя с username 'admin'? (y/n): ").strip().lower()
    if create_new == 'y':
        new_username = input("Введите username (по умолчанию 'admin'): ").strip() or 'admin'
        new_email = input("Введите email (по умолчанию 'admin@example.com'): ").strip() or 'admin@example.com'
        new_password = input("Введите пароль: ").strip()
        
        if new_password:
            # Удаляем старый пользователь с таким username, если есть
            User.objects.filter(username=new_username).exclude(email='miramgazy@gmail.com').delete()
            
            # Создаем нового
            new_user = User.objects.create_superuser(
                username=new_username,
                email=new_email,
                password=new_password
            )
            print(f"✓ Создан новый суперпользователь: {new_username}")
