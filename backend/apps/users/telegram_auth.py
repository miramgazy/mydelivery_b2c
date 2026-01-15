import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


import logging

logger = logging.getLogger(__name__)

class TelegramAuthException(AuthenticationFailed):
    pass


def validate_telegram_init_data(init_data):
    """
    Валидация данных инициализации Telegram Mini App
    """
    logger.info(f"Starting telegram init_data validation. Data length: {len(init_data) if init_data else 0}")
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured in settings")
        raise TelegramAuthException("TELEGRAM_BOT_TOKEN не настроен")

    try:
        # Парсим строку данных
        parsed_data = dict(parse_qsl(init_data))
        logger.debug(f"Parsed init_data keys: {list(parsed_data.keys())}")
    except ValueError as e:
        logger.error(f"Failed to parse init_data: {e}")
        raise TelegramAuthException("Некорректный формат данных")

    # Получаем хэш
    received_hash = parsed_data.get('hash')
    if not received_hash:
        logger.error("No hash found in init_data")
        raise TelegramAuthException("Hash не найден")

    # Удаляем хэш из данных для проверки
    auth_data = parsed_data.copy()
    del auth_data['hash']

    # Сортируем параметры
    data_check_string = '\n'.join(
        f'{key}={value}' for key, value in sorted(auth_data.items())
    )

    # Вычисляем секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=settings.TELEGRAM_BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # Вычисляем хэш
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Сравниваем хэши
    if calculated_hash != received_hash:
        logger.warning(f"Hash mismatch. Calculated: {calculated_hash[:10]}... Received: {received_hash[:10]}...")
        # raise TelegramAuthException("Неверная подпись данных") 
        # TODO: Uncomment checks after debugging if needed, but for now we want to see why it fails
        pass 
        # Note: I am NOT disabling the check, I will re-enable it immediately if this was a permanent change, 
        # but for debugging let's keep the check STRICT but LOG IT. 
        # Actually, let's keep the logic STRICT but log it.
        logger.error("Signature verification failed")
        raise TelegramAuthException("Неверная подпись данных")

    # Проверяем время (не старше 24 часов)
    auth_date = int(auth_data.get('auth_date', 0))
    current_time = time.time()
    if current_time - auth_date > 86400:
        logger.warning(f"Data expired. Auth date: {auth_date}, Current: {current_time}, Diff: {current_time - auth_date}")
        raise TelegramAuthException("Данные устарели")

    # Возвращаем данные пользователя
    user_data_str = auth_data.get('user')
    if not user_data_str:
        logger.error("No 'user' field in data")
        raise TelegramAuthException("Данные пользователя не найдены")

    try:
        user_data = json.loads(user_data_str)
        logger.info(f"Telegram auth validation successful for user_id: {user_data.get('id')}")
        return user_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode user JSON: {e}")
        raise TelegramAuthException("Некорректный формат данных пользователя")
