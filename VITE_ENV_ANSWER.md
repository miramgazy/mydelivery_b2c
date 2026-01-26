# ✅ Ответ: Нужны ли VITE переменные?

## Краткий ответ: **ДА, но с оговорками**

### Нужно добавить в .env Coolify:

```env
VITE_API_URL=/api
VITE_DEV_MODE=false
VITE_TELEGRAM_BOT_USERNAME=TG_MiniAppTest_Bot
```

## Почему:

1. **`docker-compose.coolify.yml` передает их как build args** - если их нет, сборка может упасть или использовать undefined значения

2. **Dockerfile теперь исправлен** - переменные устанавливаются как ENV, поэтому они будут доступны во время сборки Vite

3. **Для будущего использования** - даже если сейчас они не используются в коде, они могут понадобиться позже

## Значения:

- **`VITE_API_URL=/api`** - относительный путь к API (работает через nginx proxy)
- **`VITE_DEV_MODE=false`** - режим production
- **`VITE_TELEGRAM_BOT_USERNAME=TG_MiniAppTest_Bot`** - username бота (может использоваться для валидации или отладки)

## Важно:

После добавления этих переменных в Coolify, нужно **пересобрать frontend контейнер**, чтобы они применились.
