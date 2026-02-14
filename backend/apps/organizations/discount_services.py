"""
Сервис синхронизации скидок с iikoCloud API.
"""
import logging
import uuid
from decimal import Decimal
from typing import List

from django.db import transaction

from apps.organizations.models import Organization, Discount
from apps.iiko_integration.client import IikoClient, IikoAPIException

logger = logging.getLogger(__name__)


def sync_discounts_from_iiko(organization: Organization) -> dict:
    """
    Синхронизирует скидки из iikoCloud API для указанной организации.

    Логика:
    1. Получает токен через /api/1/access_token
    2. Запрашивает скидки через POST /api/1/discounts (organizationIds)
    3. Собирает все id из ответа API во временный список
    4. Все локальные скидки, чьи external_id не попали в список, помечает is_active=False
    5. Для скидок из списка выполняет update_or_create, обновляя поля и устанавливая is_active=True

    Returns:
        dict: {'synced': int, 'deactivated': int, 'error': str|None}
    """
    if not organization.api_key or not organization.iiko_organization_id:
        raise ValueError("У организации должны быть настроены api_key и iiko_organization_id")

    org_id = organization.iiko_organization_id
    client = IikoClient(organization.api_key)

    try:
        response = client.get_discounts([org_id])
    except IikoAPIException as e:
        logger.error(f"Ошибка при запросе скидок из iiko: {e}")
        raise

    discounts_data = response.get("discounts") or []
    active_external_ids = []
    synced_count = 0
    org_id_str = str(org_id).strip().lower()

    with transaction.atomic():
        # Собираем данные из ответа и выполняем update_or_create
        for org_block in discounts_data:
            api_org_id = org_block.get("organizationId")
            # Обрабатываем только блоки для нашей организации
            if api_org_id and str(api_org_id).strip().lower() != org_id_str:
                logger.debug(f"Пропуск блока организации {api_org_id} (ожидаем {org_id})")
                continue
            items = org_block.get("items") or []

            for item in items:
                external_id_str = item.get("id")
                if not external_id_str:
                    continue

                try:
                    external_id = uuid.UUID(str(external_id_str))
                except (ValueError, TypeError):
                    logger.warning(f"Некорректный ID скидки: {external_id_str}")
                    continue

                active_external_ids.append(external_id)

                name = item.get("name") or ""
                percent = item.get("percent")
                if percent is not None:
                    try:
                        percent = Decimal(str(percent))
                    except (ValueError, TypeError):
                        percent = Decimal("0")
                else:
                    percent = Decimal("0")

                mode = item.get("mode") or "Percent"
                is_manual = bool(item.get("isManual", False))
                is_deleted_in_iiko = bool(item.get("isDeleted", False))

                _, created = Discount.objects.update_or_create(
                    external_id=external_id,
                    defaults={
                        "organization": organization,
                        "name": name,
                        "percent": percent,
                        "mode": mode,
                        "is_manual": is_manual,
                        "is_deleted_in_iiko": is_deleted_in_iiko,
                        "is_active": True,
                    },
                )
                synced_count += 1

        # Помечаем неактивными скидки, которых нет в ответе API
        deactivated_count = Discount.objects.filter(
            organization=organization
        ).exclude(
            external_id__in=active_external_ids
        ).update(is_active=False)

    logger.info(
        f"Синхронизация скидок: org={organization.org_name}, "
        f"synced={synced_count}, deactivated={deactivated_count}"
    )
    return {
        "synced": synced_count,
        "deactivated": deactivated_count,
    }
