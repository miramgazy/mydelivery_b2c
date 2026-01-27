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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_all_terminals_stop_lists(self):
    """
    Периодическая задача для автоматической синхронизации стоп-листов всех активных терминалов.
    
    Проверяет каждый терминал:
    - Активен ли терминал
    - Находится ли текущее время в рабочем времени терминала
    - Прошло ли достаточно времени с последнего обновления (по stop_list_interval_min)
    
    Обновляет стоп-лист только для терминалов, которые прошли все проверки.
    """
    try:
        # Получаем все активные терминалы с настроенной организацией и API ключом
        terminals = Terminal.objects.filter(
            is_active=True,
            organization__is_active=True,
            organization__api_key__isnull=False
        ).select_related('organization')
        
        synced_count = 0
        skipped_count = 0
        error_count = 0
        
        for terminal in terminals:
            try:
                # Проверяем, нужно ли синхронизировать стоп-лист для этого терминала
                if not should_sync_stop_list(terminal):
                    skipped_count += 1
                    logger.debug(
                        f"Пропуск синхронизации стоп-листа для терминала {terminal.terminal_id}: "
                        f"не в рабочее время или не прошло достаточно времени"
                    )
                    continue
                
                # Синхронизируем стоп-лист
                if not terminal.organization.api_key:
                    logger.warning(
                        f"Пропуск терминала {terminal.terminal_id}: отсутствует API ключ организации"
                    )
                    skipped_count += 1
                    continue
                
                service = StopListSyncService(terminal.organization.api_key)
                result = service.sync_terminal_stop_list(terminal)
                
                synced_count += 1
                logger.info(
                    f"Стоп-лист синхронизирован для терминала {terminal.terminal_id}: "
                    f"создано {result.get('created', 0)}, обновлено {result.get('updated', 0)}, "
                    f"удалено {result.get('deleted', 0)}"
                )
                
            except IikoAPIException as e:
                error_count += 1
                logger.error(
                    f"Ошибка API iiko при синхронизации стоп-листа для терминала {terminal.terminal_id}: {e}",
                    exc_info=True
                )
            except Exception as e:
                error_count += 1
                logger.error(
                    f"Неожиданная ошибка при синхронизации стоп-листа для терминала {terminal.terminal_id}: {e}",
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
