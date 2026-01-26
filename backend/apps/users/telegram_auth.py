import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from apps.organizations.models import Organization


import logging

logger = logging.getLogger(__name__)

class TelegramAuthException(AuthenticationFailed):
    pass


def validate_telegram_init_data(init_data, bot_token=None):
    """
    Валидация данных инициализации Telegram Mini App
    
    Args:
        init_data: Строка initData от Telegram
        bot_token: Опциональный токен бота. Если не указан, будет попытка найти организацию по bot_username из initData
    
    Returns:
        tuple: (user_data, organization) - данные пользователя и найденная организация
    """
    logger.info(f"Starting telegram init_data validation. Data length: {len(init_data) if init_data else 0}")
    
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

    # Сортируем параметры (data_check_string нужен и для определения бота, и для финальной валидации)
    data_check_string = '\n'.join(
        f'{key}={value}' for key, value in sorted(auth_data.items())
    )

    # Определяем bot_token для валидации
    organization = None
    token_to_validate = None
    
    if bot_token:
        # Если токен передан явно, используем его
        token_to_validate = bot_token
        try:
            organization = Organization.objects.get(bot_token=bot_token, is_active=True)
            logger.info(f"Using provided bot_token, found organization: {organization.org_name}")
        except Organization.DoesNotExist:
            logger.warning(f"Organization not found for bot_token: {bot_token[:10]}...")
    else:
        # Быстрый путь (multi-bot): Telegram WebApp обычно присылает `receiver` (бот),
        # его можно извлечь из initData и определить организацию без перебора всех токенов.
        receiver_raw = auth_data.get('receiver')
        if receiver_raw:
            try:
                receiver = json.loads(receiver_raw)
                receiver_username = (receiver.get('username') or '').lstrip('@').strip()
                if receiver_username:
                    organization = Organization.objects.filter(
                        is_active=True,
                        bot_username__iexact=receiver_username
                    ).first()
                    if organization and organization.bot_token:
                        token_to_validate = organization.bot_token
                        logger.info(f"Resolved organization by receiver.username={receiver_username}: {organization.org_name}")
            except Exception as e:
                logger.debug(f"Failed to parse receiver from initData: {e}")

        # Медленный fallback: если receiver не пришел/не настроен, пытаемся подобрать токен по hash (O(N)).
        if not token_to_validate:
            active_organizations = Organization.objects.filter(
                is_active=True,
                bot_token__isnull=False
            ).exclude(bot_token='')

            logger.info(f"Trying to find organization by validating initData against {active_organizations.count()} organizations")

            for org in active_organizations:
                try:
                    test_secret_key = hmac.new(
                        key=b"WebAppData",
                        msg=org.bot_token.encode(),
                        digestmod=hashlib.sha256
                    ).digest()

                    test_calculated_hash = hmac.new(
                        key=test_secret_key,
                        msg=data_check_string.encode(),
                        digestmod=hashlib.sha256
                    ).hexdigest()

                    if test_calculated_hash == received_hash:
                        organization = org
                        token_to_validate = org.bot_token
                        logger.info(f"Found matching organization by hash: {org.org_name} (bot_username: {org.bot_username})")
                        break
                except Exception as e:
                    logger.debug(f"Error validating with org {org.org_id}: {e}")
                    continue
        
        # Если не нашли организацию, выбрасываем ошибку
        # Старый метод с единым TELEGRAM_BOT_TOKEN из settings больше не поддерживается
        if not organization:
            logger.error("Could not find organization for initData validation. Make sure bot_token is set in Organization model.")
            raise TelegramAuthException("Не удалось определить организацию и токен бота для валидации. Убедитесь, что бот настроен в базе данных.")

    # Вычисляем секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token_to_validate.encode(),
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
        logger.warning(f"Hash mismatch!")
        logger.warning(f"Calculated: {calculated_hash}")
        logger.warning(f"Received: {received_hash}")
        logger.warning(f"Using Bot Token: {token_to_validate[:5]}...{token_to_validate[-5:]}")
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
        
        return user_data, organization
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode user JSON: {e}")
        raise TelegramAuthException("Некорректный формат данных пользователя")
