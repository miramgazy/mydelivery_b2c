# 🌐 Настройка внешнего Nginx для проекта

## Текущая ситуация

Внешний nginx на хосте проксирует на порт `3008`, но это для другого проекта.

## Что нужно сделать

### 1. Узнать порт nginx контейнера проекта

В Coolify найдите порт, на который проброшен nginx контейнер вашего проекта:

```bash
# Проверка портов nginx контейнера
docker ps | grep nginx | grep w88c4ogc88gk00w8sog08skk

# Или через docker inspect
docker inspect nginx-w88c4ogc88gk00w8sog08skk-XXXXX | grep -A 10 Ports
```

### 2. Обновить конфигурацию внешнего Nginx

Создайте или обновите конфиг для `b2c-delivery.mevent.kz`:

```nginx
# /etc/nginx/sites-available/b2c-delivery.mevent.kz
server {
    listen 80;
    server_name b2c-delivery.mevent.kz;
    
    # Редирект на HTTPS
    return 301 https://$host$request_uri;
}

server {
    server_name b2c-delivery.mevent.kz;

    # Проксируем на внутренний nginx контейнера проекта
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

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/b2c-delivery.mevent.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/b2c-delivery.mevent.kz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```

### 3. Активировать конфигурацию

```bash
# Создать симлинк (если нужно)
sudo ln -s /etc/nginx/sites-available/b2c-delivery.mevent.kz /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезагрузить nginx
sudo systemctl reload nginx
# или
sudo nginx -s reload
```

## Важно

1. **Порт XXXX** - это порт, на который Coolify пробросил nginx контейнер проекта
2. Внутренний nginx контейнера уже настроен на проксирование к backend и frontend
3. Внешний nginx просто проксирует на внутренний nginx контейнера

## Проверка

```bash
# Проверка доступности
curl https://b2c-delivery.mevent.kz/api/

# Проверка frontend
curl -I https://b2c-delivery.mevent.kz/
```
