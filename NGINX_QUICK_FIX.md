# 🚀 Быстрое исправление конфигурации Nginx

## Проблемы в текущей конфигурации:

1. ❌ Первый server блок без `listen` и `server_name` - не работает
2. ❌ HTTPS блок возвращает `404` вместо проксирования запросов
3. ❌ Нет обработки Punycode домена
4. ❌ HTTP блок возвращает `404` вместо редиректа

## Решение - замените ВСЮ конфигурацию:

```bash
sudo nano /etc/nginx/sites-available/b2c-delivery.mevent.kz
```

**Удалите всё содержимое и вставьте:**

```nginx
# HTTP - редирект на HTTPS
server {
    listen 80;
    server_name b2c-delivery.mevent.kz xn--b2-delivery-toj.mevent.kz;

    # Редирект с Punycode на нормальный домен
    if ($host = "xn--b2-delivery-toj.mevent.kz") {
        return 301 https://b2c-delivery.mevent.kz$request_uri;
    }

    # Редирект на HTTPS
    return 301 https://b2c-delivery.mevent.kz$request_uri;
}

# HTTPS - основной сервер
server {
    listen 443 ssl http2;
    server_name b2c-delivery.mevent.kz xn--b2-delivery-toj.mevent.kz;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/b2c-delivery.mevent.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/b2c-delivery.mevent.kz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Редирект с Punycode на нормальный домен
    if ($host = "xn--b2-delivery-toj.mevent.kz") {
        return 301 https://b2c-delivery.mevent.kz$request_uri;
    }

    client_max_body_size 20M;

    # Проксирование на внутренний nginx контейнера проекта (порт 3090)
    location / {
        proxy_pass http://127.0.0.1:3090;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Стандартные заголовки
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        proxy_connect_timeout 75s;

        # Буферы
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # Отключение буферизации для Telegram WebView
        proxy_buffering off;
    }
}
```

## Применить изменения:

```bash
# Проверить конфигурацию
sudo nginx -t

# Если OK, перезагрузить
sudo systemctl reload nginx
```

## Что исправлено:

1. ✅ Удален некорректный первый server блок
2. ✅ HTTPS блок теперь проксирует запросы на порт 3090
3. ✅ HTTP блок редиректит на HTTPS
4. ✅ Добавлена обработка Punycode домена
5. ✅ Оба варианта домена принимаются и редиректятся на нормальный

## Проверка:

```bash
# Проверка доступности
curl -I https://b2c-delivery.mevent.kz/
curl -I https://xn--b2-delivery-toj.mevent.kz/  # Должен редиректить

# Проверка в браузере
# Откройте https://b2c-delivery.mevent.kz/
# Адрес должен оставаться нормальным, не меняться на Punycode
```
