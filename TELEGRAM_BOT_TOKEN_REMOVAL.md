# Удаление TELEGRAM_BOT_TOKEN и TELEGRAM_BOT_USERNAME из env

## Изменения

Токены Telegram ботов теперь хранятся на уровне организации в модели `Organization` (поля `bot_token` и `bot_username`). Это позволяет каждой организации иметь свой собственный бот.

### Удалено из конфигурации:

1. **docker-compose.coolify.yml**
   - Удалены переменные окружения `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME` из сервиса `backend`
   - Удален `VITE_TELEGRAM_BOT_USERNAME` из build args сервиса `frontend`

2. **backend/config/settings.py**
   - `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME` закомментированы с пояснением
   - `TELEGRAM_CONTACT_SECRET` оставлен (используется для валидации контактов)

3. **frontend/Dockerfile**
   - Удален `ARG VITE_TELEGRAM_BOT_USERNAME`
   - Удален `ENV VITE_TELEGRAM_BOT_USERNAME`

4. **env.b2c.template**
   - Удалены `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME`
   - Добавлен комментарий с пояснением

5. **backend/.env.example**
   - Удалены `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME`
   - Добавлен комментарий с пояснением

## Как настроить бота для организации:

1. Войдите в Django Admin: `https://b2c-delivery.mevent.kz/admin/`
2. Перейдите в раздел "Organizations"
3. Выберите нужную организацию
4. Заполните поля:
   - `Bot token` - токен бота от @BotFather
   - `Bot username` - username бота (например: `@MyBot`)
5. Сохраните изменения

## Важно:

- Код в `backend/apps/users/telegram_auth.py` уже обновлен для работы с токенами из базы данных
- Старый метод с единым `TELEGRAM_BOT_TOKEN` из settings больше не поддерживается
- Система автоматически определяет организацию по `bot_token` или `bot_username` из initData Telegram
