import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Order
from .services import OrderService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_to_iiko_task(self, order_id: str):
    """
    Async отправка заказа в iiko.
    Важно: дергать через transaction.on_commit в месте создания заказа,
    чтобы задача не стартовала до коммита.
    """
    try:
        order = Order.objects.select_related('organization', 'user', 'payment_type', 'terminal', 'delivery_address') \
            .prefetch_related('items__modifiers__modifier', 'items__product') \
            .get(order_id=order_id)
    except Order.DoesNotExist:
        logger.warning(f"send_order_to_iiko_task: order not found: {order_id}")
        return False

    # Проверяем, не был ли заказ уже отправлен (защита от дублирования)
    if order.sent_to_iiko_at is not None:
        logger.info(f"send_order_to_iiko_task: order {order_id} already sent to iiko at {order.sent_to_iiko_at}, skipping")
        return True

    try:
        # Логируем информацию о модификаторах перед отправкой
        logger.info(f"send_order_to_iiko_task: preparing order {order_id} for iiko")
        for item in order.items.all():
            mods_count = item.modifiers.count()
            if mods_count > 0:
                logger.info(
                    f"  Item {item.product_name} (ID: {item.product.product_id}): "
                    f"{mods_count} modifiers found"
                )
                for mod in item.modifiers.select_related('modifier').all():
                    modifier_code = mod.modifier.modifier_code if mod.modifier else None
                    logger.info(
                        f"    Modifier: {mod.modifier_name}, "
                        f"quantity: {mod.quantity}, "
                        f"modifier_code: {modifier_code}"
                    )
            else:
                logger.debug(f"  Item {item.product_name}: no modifiers")

        service = OrderService()
        return service.send_to_iiko(order)
    except Exception as exc:
        logger.error(f"send_order_to_iiko_task failed for order {order_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(ignore_result=True)
def smart_retry_and_backup_orders_task():
    """
    Умный повтор и резервный вебхук. Запускается каждые 120 секунд.
    - Заказы со статусом ERROR, созданные не более 3 минут назад: сразу отправка на резервный канал.
    - Заказы со статусом InProgress, созданные не более 10 минут назад:
      через 5 минут первый повтор, через 8 минут второй, через 10 минут или после 2 повторов — вебхук.
    """
    now = timezone.now()
    cutoff = now - timedelta(minutes=10)
    five_min = now - timedelta(minutes=5)
    eight_min = now - timedelta(minutes=8)
    error_cutoff = now - timedelta(minutes=3)

    service = OrderService()

    # Заказы со статусом «Ошибка», не старше 3 минут — сразу на резервный канал
    error_orders = Order.objects.filter(
        status=Order.STATUS_ERROR,
        created_at__gte=error_cutoff,
    ).select_related('organization').order_by('created_at')
    for order in error_orders:
        try:
            if service.send_order_to_backup_webhook(order):
                logger.info(f"smart_retry: order {order.order_id} (status=error, age<=3min) sent to backup webhook")
        except Exception as e:
            logger.exception(f"smart_retry: error sending ERROR order {order.order_id} to webhook: {e}")

    # Заказы InProgress: умный повтор и затем вебхук
    orders = Order.objects.filter(
        status=Order.STATUS_IN_PROGRESS,
        created_at__gte=cutoff,
    ).select_related('organization').order_by('created_at')

    for order in orders:
        try:
            created_at = order.created_at
            age_sec = (now - created_at).total_seconds()

            if age_sec >= 600 or order.retry_count >= 2:
                if service.send_order_to_backup_webhook(order):
                    pass
                continue
            if created_at <= eight_min and order.retry_count == 1:
                if order.query_to_iiko:
                    service.repeat_order_to_iiko(order)
                    order.refresh_from_db()
                    order.retry_count = 2
                    order.save(update_fields=['retry_count'])
                    logger.info(f"smart_retry: order {order.order_id} second retry, retry_count=2")
                else:
                    if service.send_order_to_backup_webhook(order):
                        pass
                continue
            if created_at <= five_min and order.retry_count == 0:
                if order.query_to_iiko:
                    service.repeat_order_to_iiko(order)
                    order.refresh_from_db()
                    order.retry_count = 1
                    order.save(update_fields=['retry_count'])
                    logger.info(f"smart_retry: order {order.order_id} first retry, retry_count=1")
                else:
                    if service.send_order_to_backup_webhook(order):
                        pass
        except Exception as e:
            logger.exception(f"smart_retry: error processing order {order.order_id}: {e}")
