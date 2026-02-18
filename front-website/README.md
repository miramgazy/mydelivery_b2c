# Веб-сайт доставки еды (tg-delivery B2C)

Отдельный Vue.js проект для публичного веб-сайта доставки. Mobile-first дизайн, Telegram Login Widget, динамические стили из БД.

## Запуск

### Разработка

```bash
cd front-website
npm install
npm run dev
```

Сайт: http://localhost:5174

Параметр организации: `?org=<uuid>` в URL (или `VITE_ORG_ID` в .env)

### Production (Docker)

```bash
# Из корня проекта
docker-compose up -d front-website
```

Маршрутизация: `site.domain.com` → контейнер front-website (см. nginx/coolify.conf)

## API

- `GET /api/website/styles/?org=<uuid>` — стили сайта
- `GET /api/website/menu/?org=<uuid>` — меню, категории, продукты
- `POST /api/website/telegram-login/` — авторизация через Telegram Login Widget

## Стили из БД

Таблица `website_styles` (Django Admin → Стили сайтов):
- primary_color, secondary_color, background_color
- font_family (Google Fonts)
- border_radius

CSS-переменные применяются в `:root` при загрузке.
