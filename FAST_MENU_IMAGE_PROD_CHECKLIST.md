# Чеклист: быстрое меню с картинками (прод / Coolify)

Перед пушем в git и деплоем в Coolify проверьте следующее.

## Backend
- [x] **Модель** `FastMenuGroup`: поле `image` (ImageField, upload_to='fast_menu/', blank=True, null=True)
- [x] **Миграция** `0009_fast_menu_group_image.py` — применена при `migrate`
- [x] **Pillow** в `requirements.txt` и системные пакеты (libjpeg-dev, zlib1g-dev, libpng-dev) в Dockerfile
- [x] **Сериализаторы**: `FastMenuGroupSerializer` и `FastMenuGroupPublicSerializer` отдают `image_url` (полный URL через `request.build_absolute_uri`)
- [x] **Настройки**: `USE_X_FORWARDED_HOST = True`, `MEDIA_URL = 'media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`
- [x] **Coolify**: volume `django_media:/app/media` у backend и nginx

## Nginx (coolify.conf)
- [x] **Раздача медиа**: `location /media/` → `alias /app/media/`
- [x] **Заголовки для API**: `X-Forwarded-Host $host` (чтобы Django собирал правильный URL картинок)
- [x] **Лимит загрузки**: `client_max_body_size 20M` (достаточно для изображений)

## Frontend
- [x] **API**: при отправке FormData заголовок `Content-Type` не задаётся (axios подставляет multipart с boundary)
- [x] **Админка**: загрузка файла, превью, сохранение через FormData; превью при редактировании из `getGroup()` + `normalizeMediaUrl`
- [x] **Главная TMA**: плитки с `image_url`, нормализация через `normalizeMediaUrl`
- [x] **Утилита** `utils/mediaUrl.js`: подмена хоста только для `backend` (Docker); в проде тот же origin — URL не меняется

## После деплоя в Coolify
1. **Пересобрать образ backend** (чтобы подтянуть Pillow и миграцию).
2. **Миграции** выполняются в `docker-entrypoint-coolify.sh` (`python manage.py migrate --noinput`).
3. Убедиться, что volume `django_media` общий для backend и nginx (в docker-compose.coolify.yml так и задано).
4. Проверить: создание/редактирование группы с картинкой в админке, отображение плиток на главной TMA и открытие картинки по URL в браузере.

## Если картинки не открываются в проде
- Проверить, что запросы к API идут с тем же доменом, что и фронт (иначе проверить CORS и то, что в ответах API приходит полный URL с этим доменом).
- В DevTools → Network посмотреть URL картинки в ответе API (`image_url`) и открыть его в новой вкладке.
- Убедиться, что nginx отдаёт файлы из `/app/media/` (проверить volume и права).
