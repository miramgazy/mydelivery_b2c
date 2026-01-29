import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import Q, Max

from apps.organizations.models import Terminal
from apps.iiko_integration.services import StopListSyncService, IikoAPIException

logger = logging.getLogger(__name__)


def is_working_time(terminal: Terminal) -> bool:
    """
    Проверяет, находится ли текущее время в рабочем времени терминала.
    
    Args:
        terminal: Терминал для проверки
        
    Returns:
        bool: True если текущее время в рабочем времени, False иначе
    """
    if not terminal.working_hours:
        # Если рабочее время не настроено, считаем что терминал всегда работает
        return True
    
    start_time = terminal.working_hours.get('start')
    end_time = terminal.working_hours.get('end')
    
    if not start_time or not end_time:
        # Если время не настроено полностью, считаем что терминал всегда работает
        return True
    
    try:
        # Получаем текущее время в часовом поясе проекта
        now = timezone.now()
        current_time = now.strftime('%H:%M')
        
        # Преобразуем время в минуты для удобства сравнения
        def time_to_minutes(time_str: str) -> int:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        current_minutes = time_to_minutes(current_time)
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)
        
        # Проверяем, находится ли текущее время в рабочем диапазоне
        if start_minutes <= end_minutes:
            # Обычный случай: рабочее время в пределах одного дня (например, 09:00 - 22:00)
            return start_minutes <= current_minutes < end_minutes
        else:
            # Переход через полночь (например, 18:00 - 04:00)
            # Рабочее время: с 18:00 до 23:59 или с 00:00 до 04:00
            return current_minutes >= start_minutes or current_minutes < end_minutes
    except Exception as e:
        logger.error(f"Ошибка при проверке рабочего времени терминала {terminal.terminal_id}: {e}")
        # В случае ошибки считаем что терминал работает
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
    
    Оптимизация: один запрос к iiko API на организацию вместо одного на каждый терминал —
    снижает нагрузку на API и время выполнения задачи.
    
    Проверяет каждый терминал:
    - Активен ли терминал
    - Находится ли текущее время в рабочем времени терминала
    - Прошло ли достаточно времени с последнего обновления (по stop_list_interval_min)
    """
    try:
        terminals = Terminal.objects.filter(
            is_active=True,
            organization__is_active=True,
            organization__api_key__isnull=False
        ).select_related('organization')
        
        # Оставляем только терминалы, которым нужна синхронизация
        to_sync = [t for t in terminals if should_sync_stop_list(t)]
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
