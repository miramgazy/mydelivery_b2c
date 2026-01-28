import logging

from celery import shared_task

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
