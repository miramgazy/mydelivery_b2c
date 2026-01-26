# 🔧 Исправление проблемы с Punycode доменом

## Проблема
При вводе `b2c-delivery.mevent.kz` адрес меняется на `http://xn--b2-delivery-toj.mevent.kz/`

Это происходит из-за того, что браузер интерпретирует домен как IDN (Internationalized Domain Name) и преобразует его в Punycode.

## Решение

Обновите конфигурацию внешнего nginx на хосте:

```nginx
# /etc/nginx/sites-available/b2c-delivery.mevent.kz

# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name b2c-delivery.mevent.kz xn--b2-delivery-toj.mevent.kz;

    # Редирект на HTTPS
    return 301 https://b2c-delivery.mevent.kz$request_uri;
}

# Основной HTTPS сервер
server {
    listen 443 ssl http2;
    server_name b2c-delivery.mevent.kz xn--b2-delivery-toj.mevent.kz;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/b2c-delivery.mevent.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/b2c-delivery.mevent.kz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Нормализация домена - редирект с Punycode на нормальный домен
    if ($host = "xn--b2-delivery-toj.mevent.kz") {
        return 301 https://b2c-delivery.mevent.kz$request_uri;
    }

    # Проксирование на внутренний nginx контейнера
    # ЗАМЕНИТЕ XXXX на реальный порт из Coolify
    location / {
        proxy_pass http://127.0.0.1:XXXX;
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

## Ключевые изменения:

1. **Добавлен Punycode домен в server_name**: `xn--b2-delivery-toj.mevent.kz`
2. **Добавлен редирект с Punycode на нормальный домен**: `if ($host = "xn--b2-delivery-toj.mevent.kz")`
3. **Оба варианта домена принимаются**, но Punycode редиректится на нормальный

## Применение изменений:

```bash
# Проверить конфигурацию
sudo nginx -t

# Перезагрузить nginx
sudo systemctl reload nginx
# или
sudo nginx -s reload
```

## Альтернативное решение (если проблема в DNS):

Если проблема в DNS, можно:
1. Проверить DNS записи для домена
2. Убедиться, что A запись указывает на правильный IP
3. Проверить, нет ли конфликтующих CNAME записей

## Проверка:

```bash
# Проверка DNS
dig b2c-delivery.mevent.kz
dig xn--b2-delivery-toj.mevent.kz

# Проверка доступности
curl -I https://b2c-delivery.mevent.kz/
curl -I https://xn--b2-delivery-toj.mevent.kz/
```
