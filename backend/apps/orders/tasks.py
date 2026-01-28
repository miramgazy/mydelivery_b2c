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

    try:
        service = OrderService()
        return service.send_to_iiko(order)
    except Exception as exc:
        logger.error(f"send_order_to_iiko_task failed for order {order_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

