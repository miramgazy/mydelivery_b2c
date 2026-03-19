"""
Бизнес-логика для работы с заказами
"""
import json
import logging
from copy import deepcopy
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
import random
import re
import requests
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, OrderItemModifier, IikoRequestLog
from .serializers import OrderDetailSerializer
from apps.products.models import Product, Modifier, StopList
from apps.users.models import User, DeliveryAddress, BillingPhone
from apps.organizations.models import Organization, PaymentType, Terminal
from apps.iiko_integration.client import IikoClient, IikoAPIException


logger = logging.getLogger(__name__)

# Ключи, которые НЕ перезаписываются из api_custom_params (целостность заказа)
PROTECTED_ORDER_KEYS = frozenset({'items'})


def deep_merge_iiko(
    base: Dict[str, Any],
    override: Dict[str, Any],
    protected_keys: Optional[frozenset] = None,
) -> Dict[str, Any]:
    """
    Глубокое слияние: накладывает override на base.
    Существующие ключи перезаписываются, новые добавляются.
    Для вложенного блока "order" ключи из protected_keys не перезаписываются
    (items, modifiers — формируются системой).
    """
    if not override:
        return deepcopy(base)
    result = deepcopy(base)
    _protected = protected_keys or frozenset()

    for key, override_val in override.items():
        if key in _protected:
            continue
        if key not in result:
            result[key] = deepcopy(override_val)
        elif isinstance(result[key], dict) and isinstance(override_val, dict):
            # Рекурсивное слияние для вложенных dict
            if key == 'order':
                # В блоке order защищаем items
                result[key] = deep_merge_iiko(
                    result[key], override_val, protected_keys=PROTECTED_ORDER_KEYS
                )
            else:
                result[key] = deep_merge_iiko(result[key], override_val)
        else:
            result[key] = deepcopy(override_val)
    return result


class OrderService:
    """Сервис для управления заказами"""

    @staticmethod
    def _normalize_phone(phone: Optional[str]) -> str:
        """
        Normalize phone to digits with leading '+' when possible.
        Accepts inputs like: '+7 (777) 123-45-67' -> '+77771234567'
        """
        if not phone:
            return ''
        raw = str(phone).strip()
        # keep digits only
        digits = re.sub(r'\D+', '', raw)
        if not digits:
            return ''

        # Common local formats:
        # - 8XXXXXXXXXX -> +7XXXXXXXXXX
        # - 7XXXXXXXXXX -> +7XXXXXXXXXX
        if len(digits) == 11 and digits.startswith('8'):
            digits = '7' + digits[1:]

        if raw.startswith('+'):
            return f"+{digits}"

        # If looks like country-coded number, prefix '+'
        if len(digits) >= 10:
            return f"+{digits}"

        return digits

    @staticmethod
    def _customer_name(user: User) -> str:
        """
        Best-effort customer name for iiko payload.
        """
        name = (user.full_name or '').strip()
        if name:
            return name
        if user.first_name:
            return user.first_name
        if user.telegram_username:
            return user.telegram_username
        if user.username:
            return user.username
        return "Клиент"
    
    @transaction.atomic
    def create_order(
        self,
        user: User,
        organization: Organization,
        validated_data: Dict
    ) -> Order:
        """
        Создание заказа в базе данных
        """
        # Получаем данные
        delivery_address_id = validated_data.get('delivery_address_id')
        phone = self._normalize_phone(validated_data.get('phone'))
        comment = validated_data.get('comment', '')
        remote_payment_phone = self._normalize_phone(
            validated_data.get('remote_payment_phone')
        )
        save_billing_phone = bool(validated_data.get('save_billing_phone'))
        payment_type_id = validated_data.get('payment_type_id')
        terminal_id = validated_data.get('terminal_id')
        items_data = validated_data.get('items', [])
        # Сумма доставки (если фронт её уже посчитал и передал отдельно)
        delivery_cost = validated_data.get('delivery_cost')
        
        # 1. Determine the terminal to use
        selected_terminal = None
        if terminal_id:
            try:
                selected_terminal = Terminal.objects.get(terminal_id=terminal_id)
            except Terminal.DoesNotExist:
                raise ValueError('Выбранный терминал не найден')
        else:
            # Attempt to determine automatically
            user_terminals = user.terminals.all()
            if user_terminals.count() == 1:
                selected_terminal = user_terminals.first()
            elif user_terminals.count() > 1:
                raise ValueError('Необходимо выбрать терминал (выдано более одного)')
            else:
                # No user terminals, check organization
                org_terminals = organization.terminals.all()
                if org_terminals.count() == 1:
                    selected_terminal = org_terminals.first()
                elif org_terminals.count() > 1:
                    raise ValueError('Для организации доступно несколько терминалов, выберите один')
                elif org_terminals.count() == 0:
                    raise ValueError('Для этой организации не настроены терминалы')

        if not selected_terminal:
             raise ValueError('Не удалось определить терминал для заказа')
        
        # Получаем адрес доставки если указан
        delivery_address = None
        if delivery_address_id:
            try:
                delivery_address = DeliveryAddress.objects.get(
                    id=delivery_address_id,
                    user=user
                )
            except DeliveryAddress.DoesNotExist:
                raise ValueError('Адрес доставки не найден')
        
        # Тип оплаты (может быть не указан, если не настроен)
        payment_type = None
        system_type = ''
        payment_name = 'Не указан'
        if payment_type_id:
            try:
                payment_type = PaymentType.objects.get(
                    payment_id=payment_type_id,
                    organization=organization,
                    is_active=True
                )
                system_type = (payment_type.system_type or '').strip()
                payment_name = payment_type.payment_name or 'Не указан'
            except PaymentType.DoesNotExist:
                raise ValueError('Тип оплаты не найден')

        # Конструктор комментария для персонала (блоки: Оплата, Доставка, Клиент)
        kaspi_phone = remote_payment_phone or phone

        # Блок Оплаты: Оплата: {payment_name}. Если remote_payment — выставить удаленный счет {billing_phone}
        payment_block = f"Оплата: {payment_name}"
        if system_type == 'remote_payment' and kaspi_phone:
            payment_block += f"\nвыставить удаленный счет {kaspi_phone}"

        # Блок Доставки: только при доставке (не при самовывозе)
        delivery_type = (validated_data.get('delivery_type') or 'delivery').strip().lower()
        delivery_block = None
        if delivery_type == 'delivery' and delivery_address_id:
            is_unverified = delivery_address and not delivery_address.is_verified
            unverified_msg = "Стоимость доставки не расчитан из за отсутствие геоданных."
            
            if delivery_cost is not None:
                try:
                    delivery_cost_value = Decimal(str(delivery_cost))
                    if delivery_cost_value == 0:
                        delivery_block = unverified_msg if is_unverified else "Доставка БЕСПЛАТНАЯ"
                    else:
                        delivery_block = f"Доставка ПЛАТНАЯ - сумма доставки {delivery_cost_value} ₸"
                except Exception:
                    if delivery_cost == 0 or str(delivery_cost).strip() == '0':
                        delivery_block = unverified_msg if is_unverified else "Доставка БЕСПЛАТНАЯ"
                    else:
                        delivery_block = f"Доставка ПЛАТНАЯ - сумма доставки {delivery_cost} ₸"
            else:
                delivery_block = unverified_msg if is_unverified else "Доставка БЕСПЛАТНАЯ"

        # Блок Клиента: user_comment если заполнен
        comment_parts = [payment_block]
        if delivery_block:
            comment_parts.append(delivery_block)
        if comment and str(comment).strip():
            comment_parts.append(str(comment).strip())

        final_comment = "\n".join(comment_parts)
        
        # Стоимость доставки: из запроса или 0 (бесплатно)
        delivery_cost_value = Decimal('0')
        if validated_data.get('delivery_cost') is not None:
            try:
                delivery_cost_value = Decimal(str(validated_data['delivery_cost']))
            except Exception:
                delivery_cost_value = Decimal('0')

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            organization=organization,
            status=Order.STATUS_PENDING,
            order_number=f"#TMP-{random.randint(1000, 9999)}",
            total_amount=Decimal('0'),
            delivery_cost=delivery_cost_value,
            delivery_address=delivery_address,
            phone=phone,
            comment=final_comment,
            payment_type=payment_type,
            terminal=selected_terminal,
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude')
        )

        # Если у пользователя в профиле нет телефона — сохраним из заказа (B2C UX).
        if phone and not user.phone:
            user.phone = phone
            user.save(update_fields=['phone'])

        # При удалённой оплате по Kaspi по желанию пользователя сохраняем номер в BillingPhone
        if system_type == 'remote_payment' and kaspi_phone and save_billing_phone:
            existing = BillingPhone.objects.filter(
                user=user,
                phone=kaspi_phone
            ).first()

            if existing:
                # Делаем существующий номер основным
                if not existing.is_default:
                    existing.is_default = True
                    existing.save(update_fields=['is_default'])
                    BillingPhone.objects.filter(user=user).exclude(
                        id=existing.id
                    ).update(is_default=False)
            else:
                bp = BillingPhone.objects.create(
                    user=user,
                    phone=kaspi_phone,
                    is_default=True,
                )
                BillingPhone.objects.filter(user=user).exclude(
                    id=bp.id
                ).update(is_default=False)
        
        # Продукты только из активного меню организации (product_id не уникален глобально).
        product_ids = [item_data['product_id'] for item_data in items_data]
        products_map = {
            p.product_id: p
            for p in Product.objects.prefetch_related('modifiers').filter(
                product_id__in=product_ids,
                organization=organization,
                menu__is_active=True,
            )
        }

        total_amount = Decimal('0')

        for item_data in items_data:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            modifiers_data = item_data.get('modifiers', [])
            user_selected_modifier_ids = {m.get('modifier_id') for m in modifiers_data if m.get('modifier_id')}

            product = products_map.get(product_id)
            if not product:
                order.delete()
                raise ValueError(f'Продукт {product_id} не найден')

            # Проверяем стоп-лист для выбранного терминала
            stop_list_query = StopList.objects.filter(
                product=product,
                organization=organization
            )
            if selected_terminal:
                stop_list_query = stop_list_query.filter(terminal=selected_terminal)
            if stop_list_query.exists():
                order.delete()
                raise ValueError(
                    f'Продукт "{product.product_name}" временно недоступен'
                    + (f' в филиале "{selected_terminal.terminal_group_name}"' if selected_terminal else '')
                )

            item_price = product.price
            item_total = item_price * quantity

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.product_name,
                quantity=quantity,
                price=item_price,
                total_price=item_total
            )

            # Модификаторы, выбранные пользователем (опциональные)
            for mod_data in modifiers_data:
                modifier_id = mod_data.get('modifier_id')
                mod_quantity = mod_data.get('quantity', 1)
                try:
                    modifier = Modifier.objects.get(
                        modifier_id=modifier_id,
                        product=product
                    )
                    OrderItemModifier.objects.create(
                        order_item=order_item,
                        modifier=modifier,
                        modifier_name=modifier.modifier_name,
                        quantity=mod_quantity,
                        price=modifier.price
                    )
                    item_total += modifier.price * mod_quantity * quantity
                except Modifier.DoesNotExist:
                    logger.warning(f'Модификатор {modifier_id} не найден')

            # Обязательные модификаторы (is_required или min_amount > 0): добавляем автоматически
            if product.has_modifiers:
                for mod_def in product.modifiers.all():
                    if not (mod_def.is_required or (mod_def.min_amount or 0) > 0):
                        continue
                    if mod_def.modifier_id in user_selected_modifier_ids:
                        continue
                    qty = max(1, mod_def.min_amount or 0)
                    OrderItemModifier.objects.create(
                        order_item=order_item,
                        modifier=mod_def,
                        modifier_name=mod_def.modifier_name,
                        quantity=qty,
                        price=mod_def.price
                    )
                    item_total += mod_def.price * qty * quantity

            order_item.total_price = item_total
            order_item.save(update_fields=['total_price'])
            total_amount += item_total
        
        # Обновляем общую сумму заказа
        order.total_amount = total_amount
        order.save(update_fields=['total_amount'])
        
        logger.info(f'Создан заказ {order.order_id} на сумму {total_amount}')
        
        return order
    
    def send_to_iiko(self, order: Order) -> bool:
        """
        Отправка заказа в iiko.
        Использует transaction.atomic для предотвращения отправки некорректно собранных данных.
        Итоговый склеенный JSON логируется в таблицу IikoRequestLog.
        """
        # Проверяем, не был ли заказ уже отправлен
        if order.sent_to_iiko_at is not None:
            logger.warning(
                f'Заказ {order.order_id} уже был отправлен в iiko в {order.sent_to_iiko_at}. '
                f'Пропускаем повторную отправку.'
            )
            return True

        with transaction.atomic():
            try:
                # Подготавливаем данные (код + api_custom_params)
                iiko_data = self._prepare_iiko_order_data(order)
                order.query_to_iiko = iiko_data

                # Логируем в таблицу логов до отправки (итоговый склеенный JSON)
                request_log = IikoRequestLog.objects.create(
                    order=order,
                    payload=iiko_data,
                    success=False,
                )

                # Логируем в application log
                logger.info(
                    f'Отправка заказа {order.order_id} в iiko: '
                    f'items_count={len(iiko_data.get("order", {}).get("items", []))}, '
                    f'organizationId={iiko_data.get("organizationId")}, '
                    f'terminalGroupId={iiko_data.get("terminalGroupId")}'
                )
                for item in iiko_data.get("order", {}).get("items", []):
                    if "modifiers" in item:
                        logger.info(
                            f'  Позиция {item.get("productId")}: '
                            f'{len(item["modifiers"])} модификаторов'
                        )
                logger.info(
                    f'Итоговый JSON запрос к iiko для заказа {order.order_id} (перед отправкой):\n'
                    f'{json.dumps(iiko_data, ensure_ascii=False, indent=2)}'
                )

                # Отправка
                client = IikoClient(order.organization.api_key)
                response = client.create_delivery_order(iiko_data)

                order_info = response.get('orderInfo', {})
                correlation_id = response.get('correlationId')

                order.iiko_order_id = order_info.get('id')
                order.correlation_id = correlation_id
                order.status = order_info.get('creationStatus') or Order.STATUS_IN_PROGRESS
                # iiko может вернуть номер заказа сразу при создании
                iiko_number = order_info.get('number') or order_info.get('externalNumber')
                if iiko_number:
                    order.iiko_delivery_number = str(iiko_number)
                    order.order_number = str(iiko_number)
                order.sent_to_iiko_at = timezone.now()
                order.iiko_response = response
                order.error_message = None
                order.save(update_fields=[
                    'iiko_order_id', 'correlation_id', 'status',
                    'sent_to_iiko_at', 'iiko_response', 'query_to_iiko', 'error_message',
                    'iiko_delivery_number', 'order_number',
                ])

                request_log.success = True
                request_log.save(update_fields=['success'])

                logger.info(f'Заказ {order.order_id} отправлен в iiko (correlationId: {correlation_id})')
                return True

            except IikoAPIException as e:
                logger.error(f'Ошибка отправки заказа {order.order_id} в iiko: {e}')
                order.status = Order.STATUS_ERROR
                order.error_message = str(e)
                order.save(update_fields=['status', 'error_message', 'query_to_iiko'])
                return False

            except Exception as e:
                logger.error(f'Неожиданная ошибка при отправке заказа {order.order_id}: {e}', exc_info=True)
                order.status = Order.STATUS_ERROR
                order.error_message = f'Системная ошибка: {str(e)}'
                order.save(update_fields=['status', 'error_message', 'query_to_iiko'])
                return False

    @transaction.atomic
    def repeat_order_to_iiko(self, order: Order) -> Order:
        """
        Повторно отправляет в iiko существующий заказ, используя сохранённый
        JSON-запрос в поле query_to_iiko. Новый заказ в базе не создаётся.
        """
        if not order.query_to_iiko:
            raise ValueError('У заказа отсутствует сохранённый запрос в iiko (query_to_iiko)')

        payload = order.query_to_iiko
        client = IikoClient(order.organization.api_key)

        try:
            response = client.create_delivery_order(payload)
        except IikoAPIException as e:
            logger.error(f'Повторная отправка заказа {order.order_id} в iiko: {e}')
            order.status = Order.STATUS_ERROR
            order.error_message = str(e)
            order.iiko_response = {'error': str(e)}
            order.save(update_fields=['status', 'error_message', 'iiko_response'])
            raise

        order_info = response.get('orderInfo', {})
        correlation_id = response.get('correlationId')

        order.iiko_order_id = order_info.get('id')
        order.correlation_id = correlation_id
        order.status = order_info.get('creationStatus') or Order.STATUS_IN_PROGRESS
        order.sent_to_iiko_at = timezone.now()
        order.iiko_response = response
        order.error_message = None
        order.save(update_fields=[
            'iiko_order_id', 'correlation_id', 'status',
            'sent_to_iiko_at', 'iiko_response', 'error_message'
        ])

        IikoRequestLog.objects.create(
            order=order,
            payload=payload,
            success=True,
        )

        logger.info(f'Повторная отправка заказа {order.order_id} в iiko (correlationId: {correlation_id})')
        return order

    def update_order_creation_status(self, order: Order) -> Dict:
        """
        Запрос статуса создания заказа в iiko по correlationId
        """
        if not order.correlation_id:
            raise ValueError('correlation_id отсутствует для этого заказа')
        
        try:
            client = IikoClient(order.organization.api_key)
            org_id = str(order.organization.iiko_organization_id or order.organization.org_id)
            
            status_response = client.get_creation_status(org_id, str(order.correlation_id))
            
            creation_status = status_response.get('state')  # usually 'Success', 'InProgress', 'Error'
            
            # В iiko commands/status возвращает 'state'
            # Если это deliveries/create, то в ответе может быть 'Success'
            if creation_status == 'Success':
                # Команды в iiko обычно возвращают результат в поле 'result'
                result = status_response.get('result', {})
                if isinstance(result, dict):
                    order_info = result.get('orderInfo', {}) or {}
                    # Может прийти iiko_order_id и номер
                    if not order.iiko_order_id and order_info.get('id'):
                        order.iiko_order_id = order_info.get('id')
                    iiko_number = order_info.get('number') or order_info.get('externalNumber')
                    if iiko_number:
                        order.iiko_delivery_number = str(iiko_number)
                        order.order_number = str(iiko_number)

                # По требованию: если создание успешно — назначаем реальный статус заказа из iiko
                # (например Cancelled / Cooking / Confirmed), который приходит из deliveries/by_id.
                # Если iiko_order_id уже известен — подтянем детали и применим status.
                if order.iiko_order_id:
                    self.get_order_details_and_update(order)
                else:
                    order.status = Order.STATUS_SUCCESS
            
            elif creation_status == 'Error':
                order.status = Order.STATUS_ERROR
                order.error_message = status_response.get('exception', {}).get('message', 'Неизвестная ошибка iiko')
            else:
                order.status = creation_status
            
            order.save(update_fields=[
                'status', 'iiko_delivery_number', 'error_message', 'order_number', 'iiko_order_id'
            ])
            return status_response
            
        except IikoAPIException as e:
            logger.error(f'Ошибка превращения статуса создания для {order.order_id}: {e}')
            raise

    def get_order_details_and_update(self, order: Order) -> Dict:
        """
        Получение полных деталей заказа из iiko и обновление локальных данных
        """
        if not order.iiko_order_id:
            raise ValueError('iiko_order_id отсутствует')
            
        try:
            client = IikoClient(order.organization.api_key)
            org_id = str(order.organization.iiko_organization_id or order.organization.org_id)
            
            status_data = client.get_order_status(org_id, str(order.iiko_order_id))
            
            if 'orders' in status_data and len(status_data['orders']) > 0:
                iiko_order = status_data['orders'][0] or {}
                creation_status = iiko_order.get('creationStatus')
                inner_order = iiko_order.get('order') or {}

                # Номер заказа (в ответе приходит как order.number)
                iiko_number = inner_order.get('number') or iiko_order.get('externalNumber')
                if iiko_number:
                    order.iiko_delivery_number = str(iiko_number)
                    order.order_number = str(iiko_number)

                # Два статуса:
                # - creationStatus: статус создания
                # - order.status: реальный статус заказа (Cancelled/Confirmed/Cooking/etc.)
                if str(creation_status).lower() == 'success':
                    real_status = inner_order.get('status')
                    if real_status:
                        order.status = str(real_status)
                elif creation_status:
                    order.status = str(creation_status)

                order.save(update_fields=['iiko_delivery_number', 'order_number', 'status'])
            
            return status_data
        except IikoAPIException as e:
            logger.error(f'Ошибка получения деталей заказа {order.order_id}: {e}')
            raise

    def send_order_to_backup_webhook(self, order: Order) -> bool:
        """
        Отправляет заказ на резервный вебхук организации (webhook_link).
        При успешной отправке переводит заказ в статус SentToBackupWebhook.
        Возвращает True при успехе, False если вебхук не настроен или запрос не удался.
        """
        webhook_url = (order.organization.webhook_link or '').strip()
        if not webhook_url:
            logger.debug(f'send_order_to_backup_webhook: organization {order.organization_id} has no webhook_link')
            return False
        try:
            order_full = Order.objects.select_related(
                'organization', 'user', 'payment_type', 'terminal', 'delivery_address'
            ).prefetch_related('items__modifiers__modifier', 'items__product').get(order_id=order.order_id)
            payload = OrderDetailSerializer(order_full).data
        except Order.DoesNotExist:
            logger.warning(f'send_order_to_backup_webhook: order {order.order_id} not found')
            return False
        try:
            resp = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15,
            )
            resp.raise_for_status()
            order.status = Order.STATUS_SENT_TO_BACKUP_WEBHOOK
            order.save(update_fields=['status'])
            logger.info(f'Order {order.order_id} sent to backup webhook successfully')
            return True
        except requests.RequestException as e:
            logger.warning(f'send_order_to_backup_webhook failed for order {order.order_id}: {e}')
            return False
    
    def _is_pickup(self, order: Order) -> bool:
        """Самовывоз: нет адреса доставки и нет разовых координат."""
        return not order.delivery_address and not (order.latitude and order.longitude)

    def _prepare_iiko_order_data(self, order: Order) -> Dict:
        """
        Подготовка данных заказа для отправки в iiko.
        При самовывозе: orderServiceType = DeliveryByClient, блок deliveryPoint не отправляется.
        При доставке: orderServiceType = DeliveryByCourier, передаётся deliveryPoint.
        """
        is_pickup = self._is_pickup(order)
        delivery_point = None if is_pickup else self._prepare_delivery_point(order)

        items = []
        # Всегда используем prefetch_related для надежной загрузки модификаторов
        # Это гарантирует, что модификаторы будут загружены даже если они не были загружены ранее
        # [MODIFIED] Added 'product__modifiers' to prefetch defaults from Modifier table
        order_items = order.items.prefetch_related('modifiers__modifier', 'product', 'product__modifiers').all()
        
        for order_item in order_items:
            # Собираем модификаторы для этой позиции (per-unit amounts для развёрнутого формата iiko)
            # 1. Модификаторы, выбранные пользователем (из OrderItemModifier) — уже в расчёте на одну единицу продукта
            user_selected_modifiers = {}
            for order_mod in order_item.modifiers.all():
                if not order_mod.modifier:
                    logger.warning(
                        f'Модификатор заказа {order_mod.id} для позиции "{order_item.product_name}" '
                        f'не имеет связи с Modifier. Пропускаем.'
                    )
                    continue
                
                modifier_code = str(order_mod.modifier.modifier_code).strip() if order_mod.modifier.modifier_code else None
                
                if not modifier_code or modifier_code == 'None':
                    logger.warning(
                        f'Модификатор "{order_mod.modifier_name}" (ID: {order_mod.modifier.modifier_id}) '
                        f'для продукта "{order_item.product_name}" имеет невалидный modifier_code. Пропускаем.'
                    )
                    continue
                
                # В iiko API amount для модификатора - это количество на одну единицу продукта
                # Если заказано 2 пиццы и к каждой добавлен сыр x3, то amount = 3.0 (не 6.0)
                modifier_amount = float(order_mod.quantity)

                # iiko валидирует modifiers[].amount в диапазоне [min_amount, max_amount].
                # Чтобы не слать заведомо неверные значения (из-за рассинхрона меню/ограничений),
                # делаем клип перед отправкой.
                mod_def = order_mod.modifier
                min_amt_def = float(mod_def.min_amount or 0)
                max_amt_def = float(mod_def.max_amount or 0)
                if min_amt_def < 0:
                    min_amt_def = 0.0
                if max_amt_def <= 0:
                    max_amt_def = None
                original_amount = modifier_amount
                if min_amt_def > 0 and modifier_amount < min_amt_def:
                    modifier_amount = min_amt_def
                if max_amt_def is not None and modifier_amount > max_amt_def:
                    modifier_amount = max_amt_def
                if modifier_amount != original_amount:
                    logger.warning(
                        f'Клинч amount модификатора для iiko: order={order.order_id}, '
                        f'product="{order_item.product_name}", mod="{order_mod.modifier_name}", '
                        f'productId={modifier_code}, original={original_amount}, clipped={modifier_amount}, '
                        f'allowed=[{min_amt_def or 0}..{max_amt_def if max_amt_def is not None else "inf"}]'
                    )
                
                # Проверяем, что количество положительное
                if modifier_amount <= 0:
                    logger.warning(
                        f'Модификатор "{order_mod.modifier_name}" имеет неположительное количество ({modifier_amount}). '
                        f'Пропускаем.'
                    )
                    continue
                
                # Если модификатор уже был добавлен (дубликат), суммируем количества
                if modifier_code in user_selected_modifiers:
                    existing_amount = float(user_selected_modifiers[modifier_code]['amount'] or 0)
                    new_amount = existing_amount + modifier_amount
                    if min_amt_def > 0 and new_amount < min_amt_def:
                        new_amount = min_amt_def
                    if max_amt_def is not None and new_amount > max_amt_def:
                        new_amount = max_amt_def
                    user_selected_modifiers[modifier_code]['amount'] = new_amount
                    logger.warning(
                        f'Дубликат модификатора {modifier_code} для позиции "{order_item.product_name}". '
                        f'Суммируем и клипим amount по min/max iiko.'
                    )
                else:
                    user_selected_modifiers[modifier_code] = {
                        'type': 'Product',
                        'productId': modifier_code,
                        'amount': modifier_amount
                    }
                
                logger.info(
                    f'Добавлен модификатор пользователя для заказа {order.order_id}, позиция "{order_item.product_name}": '
                    f'productId={modifier_code}, amount={modifier_amount}, '
                    f'название="{order_mod.modifier_name}"'
                )
            
            # 2. Обязательные модификаторы (is_required или min_amount > 0): добавляем в JSON для iiko (per-unit amount)
            if order_item.product.has_modifiers:
                modifiers_defined = order_item.product.modifiers.all()
                for mod_def in modifiers_defined:
                    if not (mod_def.is_required or (mod_def.min_amount or 0) > 0):
                        continue
                    modifier_code = str(mod_def.modifier_code).strip() if mod_def.modifier_code else None
                    if not modifier_code or modifier_code == 'None':
                        logger.warning(
                            f'Обязательный модификатор "{mod_def.modifier_name}" (ID: {mod_def.modifier_id}) '
                            f'для продукта "{order_item.product_name}" имеет невалидный modifier_code. Пропускаем.'
                        )
                        continue
                    min_amt = float(mod_def.min_amount or 0)
                    max_amt = float(mod_def.max_amount or 0)
                    if min_amt <= 0:
                        # Для required-ограничений без minAmount отправляем 1
                        min_amt = 1.0
                    if max_amt <= 0:
                        max_amt = min_amt
                    if min_amt > max_amt:
                        logger.warning(
                            f'Неконсистентные ограничения модификатора для iiko: order={order.order_id}, '
                            f'product="{order_item.product_name}", mod="{mod_def.modifier_name}", '
                            f'productId={modifier_code}, min={min_amt}, max={max_amt}. Отправляем max.'
                        )
                        min_amt = max_amt
                    # Для развёрнутого формата (каждая штука отдельно) — amount модификатора на одну единицу = min_amt
                    if modifier_code in user_selected_modifiers:
                        existing = float(user_selected_modifiers[modifier_code]['amount'] or 0)
                        # iiko ожидает, что amount попадёт в диапазон min..max
                        if existing < min_amt:
                            existing = min_amt
                        if existing > max_amt:
                            existing = max_amt
                        user_selected_modifiers[modifier_code]['amount'] = existing
                        continue
                    user_selected_modifiers[modifier_code] = {
                        'type': 'Product',
                        'productId': modifier_code,
                        'amount': min_amt
                    }
                    logger.info(
                        f'Добавлен обязательный модификатор для заказа {order.order_id}, позиция "{order_item.product_name}": '
                        f'productId={modifier_code}, amount={min_amt} (per unit), '
                        f'название="{mod_def.modifier_name}"'
                    )
            
            # 3. iiko принимает блюда с модификаторами только в развёрнутом виде: каждая штука — отдельный item (amount: 1, modifiers с amount: 1).
            # Блюда без модификаторов (has_modifiers=False) — одна позиция с amount = quantity.
            if order_item.product.has_modifiers:
                modifiers_list = list(user_selected_modifiers.values()) if user_selected_modifiers else []
                qty = int(order_item.quantity)
                for _ in range(qty):
                    single_item = {
                        'type': 'Product',
                        'productId': str(order_item.product.product_id),
                        'amount': 1,
                        'price': float(order_item.price)
                    }
                    if modifiers_list:
                        single_item['modifiers'] = modifiers_list
                    items.append(single_item)
                logger.info(
                    f'Заказ {order.order_id}, позиция "{order_item.product_name}" (с модификаторами): '
                    f'развёрнуто в {qty} шт., каждый с amount=1'
                )
            else:
                item_data = {
                    'type': 'Product',
                    'productId': str(order_item.product.product_id),
                    'amount': float(order_item.quantity),
                    'price': float(order_item.price)
                }
                if user_selected_modifiers:
                    item_data['modifiers'] = list(user_selected_modifiers.values())
                items.append(item_data)
        
        # Итоговый объект заказа
        terminal = order.terminal
        if not terminal:
            terminal = order.organization.terminals.first()
            
        if not terminal:
            raise ValueError(f"Order {order.order_id} has no terminal assigned")

        order_payload = {
            'orderServiceType': 'DeliveryByClient' if is_pickup else 'DeliveryByCourier',
            'customer': {
                'name': self._customer_name(order.user),
                'phone': self._normalize_phone(order.phone)
            },
            'phone': self._normalize_phone(order.phone),
            'items': items
        }
        if not is_pickup and delivery_point:
            order_payload['deliveryPoint'] = delivery_point

        if order.comment:
            order_payload['comment'] = order.comment

        order_data = {
            'organizationId': str(order.organization.iiko_organization_id or order.organization.org_id),
            'terminalGroupId': str(terminal.terminal_id),
            'order': order_payload
        }

        # Наложение кастомных параметров из админки (Deep Merge)
        custom_params = getattr(order.organization, 'api_custom_params', None)
        if custom_params and isinstance(custom_params, dict):
            order_data = deep_merge_iiko(order_data, custom_params)
            logger.debug(
                f'Применены api_custom_params для организации {order.organization.org_name}'
            )

        return order_data
    
    def _prepare_delivery_point(self, order: Order) -> Dict:
        """
        Подготовка данных точки доставки
        """
        delivery_point = {}
        
        if order.delivery_address:
            address = order.delivery_address
            
            # Формируем адрес в формате, ожидаемом iiko и согласованном с вами:
            # {
            #   "phone": "+7777...",
            #   "deliveryPoint": {
            #     "address": {
            #       "city": "Актобе",
            #       "house": "2/1",
            #       "street": { "name": "Абай" },
            #       "flat": "4",
            #       "entrance": "1",
            #       "floor": "1"
            #     }
            #   }
            # }
            address_data: Dict[str, object] = {
                'city': address.city_name
            }
            
            # Улица – только по name, без ID
            street_name = address.street_name
            if not street_name and address.street:
                # Берём человекочитаемое название улицы из справочника
                street_name = getattr(address.street, 'street_name', None) or getattr(address.street, 'name', None)
            if street_name:
                address_data['street'] = {'name': street_name}
            
            # Дом
            if address.house:
                address_data['house'] = address.house
            
            # Дополнительные поля
            if address.flat:
                address_data['flat'] = address.flat
            if address.entrance:
                address_data['entrance'] = address.entrance
            if address.floor:
                address_data['floor'] = address.floor
            if address.comment:
                address_data['comment'] = address.comment
            
            delivery_point = {'address': address_data}
            
        elif order.latitude and order.longitude:
            delivery_point = {
                'type': 'coordinates',
                'coordinates': {
                    'latitude': float(order.latitude),
                    'longitude': float(order.longitude)
                },
                'address': {
                    'city': order.organization.city or 'Алматы'
                }
            }
        
        return delivery_point

def geocode_address(address: DeliveryAddress, api_key: str) -> bool:
    """
    Геокодирование адреса через Яндекс.Карты Геокодер API.
    Обновляет модель DeliveryAddress и возвращает True при успехе.
    """
    if not api_key:
        logger.warning(f"Не задан API-ключ Яндекс.Карт для адреса {address.id}")
        return False
        
    # Собираем строку адреса для Яндекса: город, улица, номер дома
    parts = []
    city = (address.city.name if address.city else (address.city_name or '')).strip()
    if city:
        parts.append(city)
    street = (address.street_name or (address.street.street_name if address.street else '') or '').strip()
    if street:
        parts.append(street)
    house = (address.house or '').strip()
    if house:
        parts.append(house)

    address_str = ", ".join(parts)
    if not address_str:
        logger.warning(f"Геокодер: пустой адрес (id={address.id}), нечего отправлять в Яндекс")
        return False

    logger.info(f"Яндекс Геокодер запрос: address_id={address.id}, geocode='{address_str}'")
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': api_key,
        'format': 'json',
        'geocode': address_str,
        'results': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        feature_member = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
        if not feature_member:
            logger.info(f"Yandex Geocoder не нашел координаты для адреса '{address_str}' ({address.id})")
            return False
             
        geo_object = feature_member[0].get('GeoObject', {})
        point = geo_object.get('Point', {}).get('pos', '')
        
        if point:
            # Яндекс возвращает `долгота широта`
            lon, lat = point.split()
            address.longitude = Decimal(lon)
            address.latitude = Decimal(lat)
            address.is_verified = True
            address.save(update_fields=['latitude', 'longitude', 'is_verified', 'updated_at'])
            
            # Извлекаем уточненный адрес, если необходимо (пока просто логируем)
            meta_data = geo_object.get('metaDataProperty', {}).get('GeocoderMetaData', {})
            normalized_text = meta_data.get('text', '')
            
            logger.info(f"Успешно получены координаты для адреса {address.id} ('{normalized_text}'): lat={lat}, lon={lon}")
            return True
        else:
            logger.warning(f"Яндекс вернул пустые координаты для '{address_str}'")
             
    except requests.RequestException as e:
        logger.error(f"HTTP ошибка при запросе к Яндекс Геокодеру для адреса {address.id}: {e}")
    except (ValueError, IndexError, TypeError, AttributeError) as e:
        logger.error(f"Ошибка при парсинге ответа Яндекс Геокодера для адреса {address.id}: {e}")
        
    return False


def geocode_address_verbose(address: DeliveryAddress, api_key: str):
    """
    Геокодирование адреса через Яндекс.Карты Геокодер API (расширенная версия).
    Возвращает tuple(ok: bool, error_message: str|None).
    """
    if not api_key:
        msg = "Не задан API-ключ Яндекс.Карт"
        logger.warning("%s для адреса %s", msg, address.id)
        return False, msg

    parts = []
    city = (address.city.name if address.city else (address.city_name or '')).strip()
    if city:
        parts.append(city)
    street = (address.street_name or (address.street.street_name if address.street else '') or '').strip()
    if street:
        parts.append(street)
    house = (address.house or '').strip()
    if house:
        parts.append(house)

    address_str = ", ".join(parts)
    if not address_str:
        msg = "Пустой адрес: нечего отправлять в геокодер"
        logger.warning("Геокодер: %s (id=%s)", msg, address.id)
        return False, msg

    logger.info("Яндекс Геокодер (sync) запрос: address_id=%s, geocode='%s'", address.id, address_str)
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': api_key,
        'format': 'json',
        'geocode': address_str,
        'results': 1
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        # Иногда Яндекс возвращает 403/401 при невалидном ключе
        if response.status_code in (401, 403):
            msg = f"Ошибка Яндекс Геокодера: доступ запрещён (HTTP {response.status_code}). Проверьте API-ключ."
            logger.warning("%s address_id=%s", msg, address.id)
            return False, msg
        response.raise_for_status()
        data = response.json()

        feature_member = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
        if not feature_member:
            msg = "Яндекс Геокодер не нашел координаты для указанного адреса"
            logger.info("%s '%s' (%s)", msg, address_str, address.id)
            return False, msg

        geo_object = feature_member[0].get('GeoObject', {})
        point = geo_object.get('Point', {}).get('pos', '')
        if not point:
            msg = "Яндекс вернул пустые координаты"
            logger.warning("%s для '%s' (%s)", msg, address_str, address.id)
            return False, msg

        lon, lat = point.split()
        address.longitude = Decimal(lon)
        address.latitude = Decimal(lat)
        address.is_verified = True
        address.save(update_fields=['latitude', 'longitude', 'is_verified', 'updated_at'])
        return True, None

    except requests.RequestException as e:
        msg = f"HTTP ошибка при запросе к Яндекс Геокодеру: {e}"
        logger.error("%s address_id=%s", msg, address.id)
        return False, msg
    except (ValueError, IndexError, TypeError, AttributeError) as e:
        msg = f"Ошибка при обработке ответа Яндекс Геокодера: {e}"
        logger.error("%s address_id=%s", msg, address.id)
        return False, msg
