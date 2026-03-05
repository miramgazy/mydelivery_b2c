import logging
from datetime import timedelta
from typing import Optional

import requests
from celery import shared_task
from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone

from apps.organizations.models import (
    MailingTask,
    MailingStatus,
    Organization,
    MailingAudienceType,
)
from apps.users.models import User


logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"
RATE_LIMIT_PER_BATCH = 30  # максимально 30 сообщений за один запуск задачи


class TelegramForbiddenError(Exception):
    """Пользователь заблокировал бота (403 Forbidden)."""


def _send_telegram_message(bot_token: str, chat_id: int, text: str) -> bool:
    """
    Отправка сообщения в Telegram.
    Возвращает True при успехе, False при технической ошибке.
    Бросает TelegramForbiddenError при 403 (отписка).
    """
    if not bot_token:
        logger.error("Попытка отправки сообщения без bot_token")
        return False

    url = TELEGRAM_API_BASE.format(token=bot_token, method="sendMessage")
    try:
        resp = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
            },
            timeout=5,
        )
    except requests.RequestException as exc:
        logger.error("Ошибка сети при отправке сообщения в Telegram: %s", exc, exc_info=True)
        return False

    if resp.status_code == 403:
        raise TelegramForbiddenError("User blocked the bot")

    if resp.status_code != 200:
        logger.warning("Ошибка Telegram API: status=%s body=%s", resp.status_code, resp.text)
        return False

    data = resp.json()
    if not data.get("ok"):
        logger.warning("Telegram API вернул ok=false: %s", data)
        return False

    return True


def _get_mailing_recipients_qs(mailing: MailingTask):
    """
    Backward-compat wrapper (не используется напрямую).
    Оставлен для совместимости, основная логика в get_mailing_recipients_queryset.
    """
    return get_mailing_recipients_queryset(mailing.organization, mailing.audience_type)


def get_mailing_recipients_queryset(organization: Organization, audience_type: str):
    """
    Базовый queryset получателей для рассылки по организации и типу аудитории.
    Учитывает is_bot_subscribed=True, наличие chat_id и сегменты по заказам.
    """
    base_qs = User.objects.filter(
        organization=organization,
        is_bot_subscribed=True,
    ).exclude(chat_id__isnull=True)

    audience = audience_type or MailingAudienceType.ALL
    if audience == MailingAudienceType.ALL:
        return base_qs

    # Аннотация последнего заказа в рамках организации
    qs = base_qs.annotate(
        last_order_at=Max(
            'orders__created_at',
            filter=Q(orders__organization=organization),
        )
    )

    if audience == MailingAudienceType.NEWBIES:
        # Пользователи без заказов в этой организации
        return qs.filter(last_order_at__isnull=True)

    # Общий порог 30 дней
    threshold = timezone.now() - timedelta(days=30)

    if audience == MailingAudienceType.SLEEPERS_30:
        # Последний заказ более 30 дней назад
        return qs.filter(last_order_at__lt=threshold, last_order_at__isnull=False)

    if audience == MailingAudienceType.ACTIVE_30:
        # Есть заказ за последние 30 дней
        return qs.filter(last_order_at__gte=threshold)

    # На всякий случай — если пришло неизвестное значение
    return base_qs


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_mailings_scheduler(self):
    """
    Периодическая задача (Celery Beat): ищет рассылки, время которых наступило,
    и запускает их обработку.
    """
    now = timezone.now()
    candidates = MailingTask.objects.filter(
        scheduled_at__lte=now,
        status__in=[MailingStatus.SCHEDULED, MailingStatus.IN_PROGRESS],
    ).select_related("organization")

    count = 0
    for mailing in candidates:
        process_mailing_task.delay(mailing.id)
        count += 1

    if count:
        logger.info("run_mailings_scheduler: запущено задач рассылок: %s", count)
    return {"started": count}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_mailing_task(self, mailing_id: int):
    """
    Основная задача отправки рассылки.
    Работает батчами по RATE_LIMIT_PER_BATCH пользователей и при необходимости
    планирует продолжение.
    """
    try:
        with transaction.atomic():
            mailing = (
                MailingTask.objects.select_for_update()
                .select_related("organization")
                .get(id=mailing_id)
            )

            # Если рассылка уже завершена/ошибка — выходим
            if mailing.status in (MailingStatus.DONE, MailingStatus.ERROR):
                return

            # Проверяем, что у организации есть bot_token
            org: Organization = mailing.organization
            if not org or not org.bot_token:
                logger.error(
                    "process_mailing_task: у организации нет bot_token (mailing_id=%s)", mailing_id
                )
                mailing.status = MailingStatus.ERROR
                mailing.save(update_fields=["status"])
                return

            # Первый запуск: считаем получателей и переводим в IN_PROGRESS
            base_qs = get_mailing_recipients_queryset(
                mailing.organization,
                mailing.audience_type or MailingAudienceType.ALL,
            )
            if mailing.status == MailingStatus.SCHEDULED:
                mailing.total_recipients = base_qs.count()
                mailing.status = MailingStatus.IN_PROGRESS
                mailing.last_processed_user_id = None
                mailing.save(update_fields=["status", "total_recipients", "last_processed_user_id"])

            # Получаем следующую пачку пользователей
            users_qs = base_qs.order_by("id")
            if mailing.last_processed_user_id:
                users_qs = users_qs.filter(id__gt=mailing.last_processed_user_id)

            batch = list(users_qs[:RATE_LIMIT_PER_BATCH])

            if not batch:
                # Все пользователи обработаны
                mailing.status = MailingStatus.DONE
                mailing.save(update_fields=["status"])
                logger.info("process_mailing_task: mailing %s завершена", mailing_id)
                return

            # Отправляем сообщения пачкой
            for user in batch:
                # Выбираем текст по языку, по умолчанию KZ
                lang = (user.language_code or "kz").lower()
                if lang == "ru":
                    text = mailing.message_ru or mailing.message_kz or ""
                else:
                    text = mailing.message_kz or mailing.message_ru or ""
                text = text.replace("{{user_name}}", user.full_name or user.username or "")

                try:
                    ok = _send_telegram_message(org.bot_token, user.chat_id, text)
                    if ok:
                        if lang == "ru":
                            mailing.sent_ru += 1
                        else:
                            mailing.sent_kz += 1
                    else:
                        mailing.failed_count += 1
                except TelegramForbiddenError:
                    # Пользователь заблокировал бота
                    user.is_bot_subscribed = False
                    user.save(update_fields=["is_bot_subscribed"])
                    mailing.unsubscribed_count += 1
                except Exception as exc:
                    logger.error(
                        "Ошибка при отправке сообщения (mailing_id=%s, user_id=%s): %s",
                        mailing_id,
                        user.id,
                        exc,
                        exc_info=True,
                    )
                    mailing.failed_count += 1

                mailing.last_processed_user_id = user.id

            mailing.save(
                update_fields=[
                    "sent_ru",
                    "sent_kz",
                    "failed_count",
                    "unsubscribed_count",
                    "last_processed_user_id",
                    "updated_at",
                ]
            )

        # Проверяем, остались ли ещё пользователи; если да — планируем продолжение
        with transaction.atomic():
            mailing = (
                MailingTask.objects.select_for_update()
                .select_related("organization")
                .get(id=mailing_id)
            )
            if mailing.status != MailingStatus.IN_PROGRESS:
                return
            remaining_exists = _get_mailing_recipients_qs(mailing).filter(
                id__gt=mailing.last_processed_user_id
            ).exists()

        if remaining_exists:
            # Планируем следующее продолжение почти сразу, чтобы не ждать минуту
            process_mailing_task.apply_async(args=[mailing_id], countdown=1)

    except Exception as exc:
        logger.error("process_mailing_task: критическая ошибка: %s", exc, exc_info=True)
        try:
            mailing = MailingTask.objects.get(id=mailing_id)
            mailing.status = MailingStatus.ERROR
            mailing.save(update_fields=["status"])
        except Exception:  # noqa: BLE001
            pass
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_mailing_test_to_chat(self, mailing_id: int, chat_id: int):
    """
    Отправка тестового сообщения на указанный chat_id без изменения данных пользователя.
    """
    try:
        mailing = MailingTask.objects.select_related("organization").get(id=mailing_id)
    except MailingTask.DoesNotExist:
        logger.warning("send_mailing_test_to_chat: mailing %s not found", mailing_id)
        return False

    org = mailing.organization
    if not org or not org.bot_token:
        logger.warning(
            "send_mailing_test_to_chat: organization or bot_token missing for mailing %s",
            mailing_id,
        )
        return False

    # Для теста используем приоритетно RU, затем KZ
    text = mailing.message_ru or mailing.message_kz or ""
    text = text.replace("{{user_name}}", "Тестовый пользователь")

    try:
        ok = _send_telegram_message(org.bot_token, chat_id, text)
        return ok
    except TelegramForbiddenError:
        logger.info("send_mailing_test_to_chat: chat_id %s blocked bot", chat_id)
        return False
    except Exception as exc:
        logger.error(
            "send_mailing_test_to_chat: error for chat_id=%s mailing_id=%s: %s",
            chat_id,
            mailing_id,
            exc,
            exc_info=True,
        )
        raise self.retry(exc=exc)

