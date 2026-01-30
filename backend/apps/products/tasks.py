import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Max

from apps.organizations.models import Terminal
from apps.iiko_integration.services import StopListSyncService, IikoAPIException

logger = logging.getLogger(__name__)


def _time_to_minutes(time_str: str) -> int:
    """Преобразует время 'HH:mm' в минуты от полуночи."""
    parts = time_str.strip().split(':')
    hours = int(parts[0]) if parts else 0
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return hours * 60 + minutes


def is_time_in_working_window(start_str: str, end_str: str) -> bool:
    """
    Проверяет, находится ли текущее время в часовом поясе проекта (TIME_ZONE) в окне [start_str, end_str].
    Используется для глобальной проверки «рабочего» времени и для терминалов без своих working_hours.
    """
    if not start_str or not end_str:
        return True
    try:
        # Локальное время проекта (TIME_ZONE), не UTC
        now = timezone.localtime(timezone.now())
        current_time = now.strftime('%H:%M')
        current_minutes = _time_to_minutes(current_time)
        start_minutes = _time_to_minutes(start_str)
        end_minutes = _time_to_minutes(end_str)
        if start_minutes <= end_minutes:
            return start_minutes <= current_minutes <= end_minutes
        # через полночь (например 22:00 — 06:00)
        return current_minutes >= start_minutes or current_minutes <= end_minutes
    except Exception as e:
        logger.warning(f"Ошибка проверки рабочего окна [{start_str}-{end_str}]: {e}")
        return True


def is_global_sync_allowed() -> bool:
    """
    Разрешена ли сейчас синхронизация стоп-листов по глобальному окну (часовой пояс сервера).
    Вне рабочего времени запросы не отправляются.
    """
    start = getattr(settings, 'STOP_LIST_SYNC_WORKING_START', None)
    end = getattr(settings, 'STOP_LIST_SYNC_WORKING_END', None)
    if not start or not end:
        return True
    return is_time_in_working_window(start, end)


def is_working_time(terminal: Terminal) -> bool:
    """
    Проверяет, находится ли текущее время сервера (TIME_ZONE, например +5) в рабочем времени терминала.
    Если у терминала не задано working_hours — используется глобальное окно из настроек
    (STOP_LIST_SYNC_WORKING_START / STOP_LIST_SYNC_WORKING_END), чтобы не слать запросы ночью.
    """
    start_time = None
    end_time = None
    if terminal.working_hours:
        start_time = terminal.working_hours.get('start')
        end_time = terminal.working_hours.get('end')
    if not start_time or not end_time:
        # Нет своих часов — используем глобальное окно (по умолчанию 08:00–23:59)
        start_time = getattr(settings, 'STOP_LIST_SYNC_WORKING_START', None)
        end_time = getattr(settings, 'STOP_LIST_SYNC_WORKING_END', None)
        if not start_time or not end_time:
            return True
    try:
        return is_time_in_working_window(start_time, end_time)
    except Exception as e:
        logger.error(f"Ошибка при проверке рабочего времени терминала {terminal.terminal_id}: {e}")
        return True


def should_sync_stop_list(terminal: Terminal) -> bool:
    """
    Проверяет, нужно ли синхронизировать стоп-лист для терминала.
    
    Проверяет:
    1. Терминал активен
    2. Текущее время в рабочем времени терминала
    3. Прошло ли достаточно времени с последнего обновления (по stop_list_interval_min)
    
    Args:
        terminal: Терминал для проверки
        
    Returns:
        bool: True если нужно синхронизировать, False иначе
    """
    # Проверяем, активен ли терминал
    if not terminal.is_active:
        return False
    
    # Проверяем рабочее время
    if not is_working_time(terminal):
        return False
    
    # Проверяем интервал обновления
    interval_minutes = terminal.stop_list_interval_min or 30
    
    # Получаем последнее обновление стоп-листа для терминала
    # Используем максимальное время updated_at из записей стоп-листа
    from apps.products.models import StopList
    last_update = StopList.objects.filter(
        terminal=terminal
    ).aggregate(
        max_updated_at=Max('updated_at')
    )['max_updated_at']
    
    # Если записей стоп-листа еще нет, нужно обновить
    if not last_update:
        return True
    
    # Проверяем, прошло ли достаточно времени с последнего обновления
    time_since_update = timezone.now() - last_update
    if time_since_update < timedelta(minutes=interval_minutes):
        return False
    
    return True


def _group_terminals_by_organization(terminals):
    """Группирует терминалы по организации (по organization_id). Возвращает dict[org_id, list[Terminal]]."""
    by_org = {}
    for t in terminals:
        org_id = t.organization_id
        if org_id not in by_org:
            by_org[org_id] = []
        by_org[org_id].append(t)
    return by_org


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_all_terminals_stop_lists(self):
    """
    Периодическая задача для автоматической синхронизации стоп-листов всех активных терминалов.
    
    Запросы отправляются только в рабочее время (часовой пояс сервера = TIME_ZONE, например +5).
    Вне глобального окна (STOP_LIST_SYNC_WORKING_START/END) задача сразу завершается без запросов.
    Для каждого терминала дополнительно учитывается working_hours (или то же глобальное окно).
    """
    try:
        # Глобальная проверка: вне рабочего времени запросы не отправляем
        if not is_global_sync_allowed():
            now_local = timezone.localtime(timezone.now())
            logger.debug(
                f"Синхронизация стоп-листов пропущена: вне рабочего времени "
                f"(локально: {now_local.strftime('%H:%M')} {getattr(settings, 'TIME_ZONE', '')})"
            )
            return {'synced': 0, 'skipped': 0, 'errors': 0, 'reason': 'outside_working_hours'}

        # Только активные терминалы и активные организации с API-ключом
        terminals = Terminal.objects.filter(
            is_active=True,
            organization__is_active=True,
            organization__api_key__isnull=False
        ).select_related('organization')
        
        # Синхронизация только для активных терминалов, прошедших проверки (время, интервал)
        to_sync = [t for t in terminals if t.is_active and should_sync_stop_list(t)]
        skipped_count = len(terminals) - len(to_sync)
        synced_count = 0
        error_count = 0
        
        # Группируем по организации: один запрос к API на организацию
        by_org = _group_terminals_by_organization(to_sync)
        
        for org_id, org_terminals in by_org.items():
            if not org_terminals:
                continue
            api_key = org_terminals[0].organization.api_key
            if not api_key:
                skipped_count += len(org_terminals)
                continue
            try:
                service = StopListSyncService(api_key)
                results = service.sync_stop_lists_for_terminals(org_terminals)
                synced_count += len(results)
                logger.info(
                    f"Стоп-листы для организации (терминалов {len(org_terminals)}): "
                    f"обработано {len(results)}"
                )
            except IikoAPIException as e:
                error_count += len(org_terminals)
                logger.error(
                    f"Ошибка API iiko при синхронизации стоп-листов организации: {e}",
                    exc_info=True
                )
            except Exception as e:
                error_count += len(org_terminals)
                logger.error(
                    f"Неожиданная ошибка при синхронизации стоп-листов организации: {e}",
                    exc_info=True
                )
        
        logger.info(
            f"Завершена синхронизация стоп-листов: синхронизировано {synced_count}, "
            f"пропущено {skipped_count}, ошибок {error_count}"
        )
        
        return {
            'synced': synced_count,
            'skipped': skipped_count,
            'errors': error_count
        }
        
    except Exception as exc:
        logger.error(f"Критическая ошибка в задаче sync_all_terminals_stop_lists: {exc}", exc_info=True)
        raise self.retry(exc=exc)
