# 🌐 Настройка Nginx для iiko Delivery System

## Архитектура с Nginx

```
                    ┌─────────────┐
                    │   Клиент    │
                    │  (Browser)  │
                    └──────┬──────┘
                           │
                           │ HTTP/HTTPS
                           ↓
                    ┌─────────────┐
                    │    Nginx    │
                    │   (Port 80) │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ↓              ↓              ↓
      ┌─────────┐    ┌─────────┐   ┌─────────┐
      │ Frontend│    │ Backend │   │  Media  │
      │  (Vue)  │    │(Django) │   │  Static │
      │Port 5173│    │Port 8000│   │  Files  │
      └─────────┘    └─────────┘   └─────────┘
```

## Что делает Nginx

1. **Reverse Proxy** - проксирует запросы к backend и frontend
2. **Static Files** - отдает статику и медиа файлы напрямую (быстрее)
3. **SSL/TLS** - терминирует HTTPS соединения
4. **Gzip/Brotli** - сжимает ответы для экономии трафика
5. **Rate Limiting** - защищает от DDoS и брутфорса
6. **Caching** - кэширует статику
7. **Load Balancing** - распределяет нагрузку (если несколько backend)

## Маршрутизация запросов

| Запрос | Куда идет | Описание |
|--------|-----------|----------|
| `/api/*` | Backend (Django) | REST API endpoints |
| `/admin/*` | Backend (Django) | Django Admin панель |
| `/static/*` | Nginx → Volume | Статика Django |
| `/media/*` | Nginx → Volume | Медиа файлы |
| `/*` | Frontend (Vue) | Все остальное → SPA |

## Запуск с Nginx

### Development режим

```bash
# 1. Запустить все сервисы включая Nginx
make up

# 2. Проверить что все работает
curl http://localhost/health  # Должен вернуть "healthy"

# 3. Доступ к сервисам
# Frontend: http://localhost/
# Backend API: http://localhost/api/
# Django Admin: http://localhost/admin/
# Swagger: http://localhost/api/schema/swagger-ui/
```

### Production режим

```bash
# 1. Собрать production образы
make prod-build

# 2. Запустить в production
make prod-up

# 3. Проверить логи
make prod-logs
```

## Конфигурации Nginx

### nginx.conf (Development)

Используется для разработки:
- Проксирует к Vite dev server (с HMR)
- Проксирует API к Django
- Отдает статику Django

### nginx.prod.conf (Production)

Используется для продакшена:
- Отдает собранный Vue build
- HTTPS с SSL сертификатами
- Rate limiting
- Gzip compression
- Security headers
- Кэширование

## SSL сертификаты (Let's Encrypt)

### Автоматическое получение

```bash
# Получить сертификат для вашего домена
make ssl-init

# Введите домен: example.com
# Введите email: admin@example.com
```

### Ручная настройка

```bash
# 1. Создать директории
mkdir -p certbot/conf certbot/www

# 2. Получить сертификат
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d example.com \
  -d www.example.com

# 3. Обновить nginx.prod.conf
# Заменить your-domain.com на ваш домен

# 4. Перезапустить Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Автоматическое обновление сертификата

Certbot контейнер автоматически обновляет сертификаты каждые 12 часов.

## Проверка конфигурации Nginx

```bash
# Проверить синтаксис конфигурации
docker-compose exec nginx nginx -t

# Перезагрузить конфигурацию без даунтайма
docker-compose exec nginx nginx -s reload
```

## Отладка проблем с Nginx

### Логи

```bash
# Просмотр логов Nginx
make logs-nginx

# Только ошибки
docker-compose exec nginx tail -f /var/log/nginx/error.log

# Только access логи
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

### Типичные проблемы

#### 1. 502 Bad Gateway

**Причина**: Backend не отвечает

**Решение**:
```bash
# Проверить что backend запущен
docker-compose ps backend

# Проверить логи backend
make logs-backend

# Перезапустить backend
docker-compose restart backend
```

#### 2. 404 на статике

**Причина**: Статика не собрана или volumes не подключены

**Решение**:
```bash
# Собрать статику Django
make collectstatic

# Проверить volumes
docker-compose exec nginx ls -la /app/staticfiles

# Пересобрать
make rebuild
```

#### 3. CORS ошибки

**Причина**: Неправильные заголовки CORS

**Решение**:
```bash
# Проверить что CORS_ALLOWED_ORIGINS включает ваш домен
# в backend/.env

# Для dev:
CORS_ALLOWED_ORIGINS=http://localhost

# Для prod:
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

## Rate Limiting

В production конфигурации включен rate limiting:

```nginx
# API - 10 запросов в секунду
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Логин - 5 запросов в минуту
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
```

### Настройка лимитов

Отредактируйте `nginx.prod.conf`:

```nginx
# Увеличить лимит для API
location /api/ {
    limit_req zone=api_limit burst=50 nodelay;  # Было burst=20
    ...
}

# Более строгий лимит для логина
location /api/auth/telegram/ {
    limit_req zone=login_limit burst=1 nodelay;  # Было burst=3
    ...
}
```

## Performance оптимизация

### Кэширование

```nginx
# Статика - кэшируется на 1 год
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Медиа - кэшируется на 30 дней
location /media/ {
    expires 30d;
    add_header Cache-Control "public";
}

# HTML - не кэшируется (SPA)
location / {
    expires -1;
    add_header Cache-Control "no-store";
}
```

### Gzip Compression

Уже включен в конфигурации:
- Сжимает текстовые файлы (HTML, CSS, JS, JSON)
- Не сжимает изображения (они уже сжаты)
- Экономит ~70% трафика

### HTTP/2

Включен в production:
```nginx
listen 443 ssl http2;
```

Преимущества:
- Множественные запросы по одному соединению
- Server push
- Сжатие заголовков

## Мониторинг Nginx

### Метрики

```bash
# Статус Nginx
curl http://localhost/health

# Статистика (если включен stub_status)
curl http://localhost/nginx_status
```

### Prometheus интеграция (опционально)

Добавьте nginx-prometheus-exporter:

```yaml
# docker-compose.prod.yml
nginx-exporter:
  image: nginx/nginx-prometheus-exporter:latest
  container_name: nginx_exporter
  command:
    - '-nginx.scrape-uri=http://nginx:80/nginx_status'
  ports:
    - "9113:9113"
  depends_on:
    - nginx
  networks:
    - iiko_network
```

## Security Headers

Production конфигурация включает:

```nginx
# HSTS - принудительный HTTPS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

# Защита от clickjacking
add_header X-Frame-Options "SAMEORIGIN";

# Защита от MIME sniffing
add_header X-Content-Type-Options "nosniff";

# XSS Protection
add_header X-XSS-Protection "1; mode=block";

# Content Security Policy
add_header Content-Security-Policy "default-src 'self' https:";
```

## Масштабирование

### Несколько backend инстансов

```nginx
upstream backend {
    least_conn;  # Или ip_hash для sticky sessions
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    keepalive 64;
}
```

### Health checks

```nginx
upstream backend {
    server backend:8000 max_fails=3 fail_timeout=30s;
}
```

## Checklist перед production

- [ ] Получен SSL сертификат
- [ ] Домен указан в nginx.prod.conf
- [ ] CORS настроен в backend
- [ ] Rate limiting настроен
- [ ] Static файлы собраны
- [ ] Frontend собран (npm run build)
- [ ] Логи настроены
- [ ] Мониторинг настроен
- [ ] Бэкапы настроены
- [ ] Firewall настроен (только 80, 443)

## Полезные команды

```bash
# Проверить все endpoints
curl http://localhost/health                    # Health check
curl http://localhost/api/                      # API root
curl -I http://localhost/static/admin/css/base.css  # Static files

# Тест производительности
ab -n 1000 -c 10 http://localhost/api/products/

# Тест SSL
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Проверить заголовки безопасности
curl -I https://your-domain.com/
```

## Troubleshooting

### Nginx не стартует

```bash
# Проверить синтаксис
docker-compose exec nginx nginx -t

# Проверить порты
netstat -tulpn | grep :80
lsof -i :80

# Проверить логи
docker-compose logs nginx
```

### Медленные запросы

```bash
# Включить slow log в nginx.conf
error_log /var/log/nginx/error.log warn;
access_log /var/log/nginx/access.log combined;

# Проверить upstream timing
tail -f /var/log/nginx/access.log | grep "upstream_response_time"
```

### Высокая нагрузка

```bash
# Проверить метрики
docker stats

# Увеличить worker_connections
# В nginx.conf:
events {
    worker_connections 2048;  # Было 1024
}

# Добавить кэширование
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
```