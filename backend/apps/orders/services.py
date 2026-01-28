"""
Бизнес-логика для работы с заказами
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Union
import random
import re
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, OrderItemModifier
from apps.products.models import Product, Modifier, StopList
from apps.users.models import User, DeliveryAddress, BillingPhone
from apps.organizations.models import Organization, PaymentType, Terminal
from apps.iiko_integration.client import IikoClient, IikoAPIException


logger = logging.getLogger(__name__)


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
        
        # Получаем тип оплаты
        try:
            payment_type = PaymentType.objects.get(
                payment_id=payment_type_id,
                organization=organization,
                is_active=True
            )
        except PaymentType.DoesNotExist:
            raise ValueError('Тип оплаты не найден')

        # Собираем комментарий об оплате для передачи в iiko
        kaspi_phone = remote_payment_phone or phone
        payment_comment = None
        delivery_comment = None

        system_type = (payment_type.system_type or '').strip()
        payment_name = payment_type.payment_name or 'Не указан'

        # Формируем комментарий об оплате
        if system_type == 'remote_payment':
            # Удалённый счёт (Kaspi) - с номером телефона для выставления счета
            if kaspi_phone:
                payment_comment = f"Оплата: {payment_name}\nвыставить удаленный счет {kaspi_phone}"
            else:
                payment_comment = f"Оплата: {payment_name}"
        elif system_type == 'cash':
            # Наличными - только название типа оплаты
            payment_comment = f"Оплата: {payment_name}"
        else:
            # Для других типов оплаты (card_on_delivery и т.д.) - только название
            payment_comment = f"Оплата: {payment_name}"

        # Информация о доставке (бесплатная/платная и сумма)
        if delivery_cost is not None:
            try:
                delivery_cost_value = Decimal(str(delivery_cost))
                if delivery_cost_value == 0:
                    delivery_comment = "Доставка БЕСПЛАТНАЯ"
                else:
                    delivery_comment = f"Доставка ПЛАТНАЯ - сумма доставки {delivery_cost_value} ₸"
            except Exception:
                # Если не получилось сконвертировать — всё равно добавим «как есть»
                if delivery_cost == 0 or str(delivery_cost).strip() == '0':
                    delivery_comment = "Доставка БЕСПЛАТНАЯ"
                else:
                    delivery_comment = f"Доставка ПЛАТНАЯ - сумма доставки {delivery_cost} ₸"

        # Собираем финальный комментарий в удобочитаемом виде:
        # 1) строка про оплату
        # 2) строка про сумму доставки (если есть)
        # 3) пользовательский комментарий (если есть)
        comment_parts = [payment_comment]
        if delivery_comment:
            comment_parts.append(delivery_comment)
        if comment:
            comment_parts.append(comment)

        final_comment = "\n".join(part for part in comment_parts if part)
        
        # Создаем заказ
        order = Order.objects.create(
            user=user,
            organization=organization,
            status=Order.STATUS_PENDING,
            order_number=f"#TMP-{random.randint(1000, 9999)}",
            total_amount=Decimal('0'),
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
        
        # Создаем позиции заказа
        total_amount = Decimal('0')
        
        for item_data in items_data:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            modifiers_data = item_data.get('modifiers', [])
            
            # Получаем продукт
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
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
            
            # Создаем позицию заказа
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
            
            # Добавляем модификаторы
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
                    
                    # Добавляем стоимость модификатора
                    item_total += modifier.price * mod_quantity * quantity
                    
                except Modifier.DoesNotExist:
                    logger.warning(f'Модификатор {modifier_id} не найден')
            
            # Обновляем итоговую сумму позиции
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
        Отправка заказа в iiko
        """
        # Проверяем, не был ли заказ уже отправлен
        if order.sent_to_iiko_at is not None:
            logger.warning(
                f'Заказ {order.order_id} уже был отправлен в iiko в {order.sent_to_iiko_at}. '
                f'Пропускаем повторную отправку.'
            )
            return True
        
        try:
            # Подготавливаем данные для iiko
            iiko_data = self._prepare_iiko_order_data(order)
            # Сохраняем полный запрос, который отправляем в iiko, для последующей диагностики
            order.query_to_iiko = iiko_data
            
            # Логируем подготовленные данные для отладки (без чувствительных данных)
            logger.info(
                f'Отправка заказа {order.order_id} в iiko: '
                f'items_count={len(iiko_data.get("order", {}).get("items", []))}, '
                f'organizationId={iiko_data.get("organizationId")}, '
                f'terminalGroupId={iiko_data.get("terminalGroupId")}'
            )
            
            # Логируем детали модификаторов
            for item in iiko_data.get("order", {}).get("items", []):
                if "modifiers" in item:
                    logger.info(
                        f'  Позиция {item.get("productId")}: '
                        f'{len(item["modifiers"])} модификаторов: '
                        f'{[m.get("productId") for m in item["modifiers"]]}'
                    )
            
            # Логируем полный JSON запрос (для отладки)
            import json
            logger.info(
                f'Полный JSON запрос для заказа {order.order_id}:\n'
                f'{json.dumps(iiko_data, ensure_ascii=False, indent=2)}'
            )
            
            # Создаем клиент iiko
            client = IikoClient(order.organization.api_key)
            # Отправляем заказ
            response = client.create_delivery_order(iiko_data)
            
            # iiko returns order status info
            order_info = response.get('orderInfo', {})
            correlation_id = response.get('correlationId')
            
            # Обновляем заказ
            order.iiko_order_id = order_info.get('id')
            order.correlation_id = correlation_id
            order.status = order_info.get('creationStatus') or Order.STATUS_IN_PROGRESS
            order.sent_to_iiko_at = timezone.now()
            order.iiko_response = response
            order.error_message = None
            order.save(update_fields=[
                'iiko_order_id', 'correlation_id', 'status',
                'sent_to_iiko_at', 'iiko_response', 'query_to_iiko', 'error_message'
            ])
            
            logger.info(f'Заказ {order.order_id} отправлен в iiko (correlationId: {correlation_id})')
            return True
                
        except IikoAPIException as e:
            logger.error(f'Ошибка отправки заказа {order.order_id} в iiko: {e}')
            
            # Сохраняем ошибку
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
            
            creation_status = status_response.get('state') # usually 'Success', 'InProgress', 'Error'
            
            # В iiko commands/status возвращает 'state'
            # Если это deliveries/create, то в ответе может быть 'Success'
            if creation_status == 'Success':
                 # Если успех, пытаемся получить детали заказа
                 order.status = Order.STATUS_SUCCESS
                 
                 # Пытаемся вытащить номер доставки если он есть в ответе
                 # Команды в iiko обычно возвращают результат в поле 'result'
                 result = status_response.get('result', {})
                 if isinstance(result, dict):
                     order_info = result.get('orderInfo', {})
                     order.iiko_delivery_number = order_info.get('number') or order_info.get('externalNumber')
            
            elif creation_status == 'Error':
                order.status = Order.STATUS_ERROR
                order.error_message = status_response.get('exception', {}).get('message', 'Неизвестная ошибка iiko')
            else:
                order.status = creation_status
            
            order.save(update_fields=['status', 'iiko_delivery_number', 'error_message'])
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
                iiko_order = status_data['orders'][0]
                # Обновляем номер если он появился
                order.iiko_delivery_number = iiko_order.get('number')
                # Здесь можно добавить маппинг статусов доставки (New, Waiting, Cooking, etc.)
                # order.status = ...
                order.save(update_fields=['iiko_delivery_number'])
            
            return status_data
        except IikoAPIException as e:
            logger.error(f'Ошибка получения деталей заказа {order.order_id}: {e}')
            raise
    
    def _prepare_iiko_order_data(self, order: Order) -> Dict:
        """
        Подготовка данных заказа для отправки в iiko
        """
        delivery_point = self._prepare_delivery_point(order)
        
        items = []
        # Всегда используем prefetch_related для надежной загрузки модификаторов
        # Это гарантирует, что модификаторы будут загружены даже если они не были загружены ранее
        # [MODIFIED] Added 'product__modifiers' to prefetch defaults from Modifier table
        order_items = order.items.prefetch_related('modifiers__modifier', 'product', 'product__modifiers').all()
        
        for order_item in order_items:
            item_data = {
                'type': 'Product',
                'productId': str(order_item.product.product_id),
                'amount': float(order_item.quantity),
                'price': float(order_item.price)
            }
            
            # Собираем модификаторы для этой позиции
            modifiers_list = []
            
            # 1. Сначала добавляем модификаторы, которые были выбраны пользователем (из OrderItemModifier)
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
                
                # Проверяем, что количество положительное
                if modifier_amount <= 0:
                    logger.warning(
                        f'Модификатор "{order_mod.modifier_name}" имеет неположительное количество ({modifier_amount}). '
                        f'Пропускаем.'
                    )
                    continue
                
                # Если модификатор уже был добавлен (дубликат), суммируем количества
                if modifier_code in user_selected_modifiers:
                    user_selected_modifiers[modifier_code]['amount'] += modifier_amount
                    logger.warning(
                        f'Дубликат модификатора {modifier_code} для позиции "{order_item.product_name}". '
                        f'Суммируем количества: {user_selected_modifiers[modifier_code]["amount"] - modifier_amount} + {modifier_amount} = {user_selected_modifiers[modifier_code]["amount"]}'
                    )
                else:
                    user_selected_modifiers[modifier_code] = {
                        'productId': modifier_code,
                        'amount': modifier_amount
                    }
                
                logger.info(
                    f'Добавлен модификатор пользователя для заказа {order.order_id}, позиция "{order_item.product_name}": '
                    f'productId={modifier_code}, amount={modifier_amount}, '
                    f'название="{order_mod.modifier_name}"'
                )
            
            # 2. Затем добавляем обязательные модификаторы (min_amount > 0), которые не были выбраны пользователем
            if order_item.product.has_modifiers:
                modifiers_defined = order_item.product.modifiers.all()
                
                for mod_def in modifiers_defined:
                    # Пропускаем, если min_amount = 0 (необязательный модификатор)
                    if mod_def.min_amount <= 0:
                        continue
                    
                    modifier_code = str(mod_def.modifier_code).strip() if mod_def.modifier_code else None
                    
                    if not modifier_code or modifier_code == 'None':
                        logger.warning(
                            f'Обязательный модификатор "{mod_def.modifier_name}" (ID: {mod_def.modifier_id}) '
                            f'для продукта "{order_item.product_name}" имеет невалидный modifier_code. Пропускаем.'
                        )
                        continue
                    
                    # Если пользователь уже выбрал этот модификатор, пропускаем
                    if modifier_code in user_selected_modifiers:
                        # Проверяем, что количество не меньше минимального
                        if user_selected_modifiers[modifier_code]['amount'] < mod_def.min_amount:
                            logger.warning(
                                f'Количество модификатора {modifier_code} ({user_selected_modifiers[modifier_code]["amount"]}) '
                                f'меньше минимального ({mod_def.min_amount}). Увеличиваем до минимума.'
                            )
                            user_selected_modifiers[modifier_code]['amount'] = float(mod_def.min_amount)
                        continue
                    
                    # Добавляем обязательный модификатор с минимальным количеством
                    # В iiko API amount - это количество на одну единицу продукта
                    modifier_amount = float(mod_def.min_amount)
                    
                    user_selected_modifiers[modifier_code] = {
                        'productId': modifier_code,
                        'amount': modifier_amount
                    }
                    
                    logger.info(
                        f'Добавлен обязательный модификатор для заказа {order.order_id}, позиция "{order_item.product_name}": '
                        f'productId={modifier_code}, amount={modifier_amount} (min_amount={mod_def.min_amount}), '
                        f'название="{mod_def.modifier_name}"'
                    )
            
            # 3. Формируем финальный список модификаторов
            if user_selected_modifiers:
                modifiers_list = list(user_selected_modifiers.values())
                item_data['modifiers'] = modifiers_list
                logger.info(
                    f'Заказ {order.order_id}, позиция "{order_item.product_name}": '
                    f'добавлено {len(modifiers_list)} модификаторов'
                )
            
            items.append(item_data)
        
        # Итоговый объект заказа
        terminal = order.terminal
        if not terminal:
            terminal = order.organization.terminals.first()
            
        if not terminal:
            raise ValueError(f"Order {order.order_id} has no terminal assigned")

        order_data = {
            'organizationId': str(order.organization.iiko_organization_id or order.organization.org_id),
            'terminalGroupId': str(terminal.terminal_id),
            'order': {
                'orderServiceType': 'DeliveryByCourier',
                'customer': {
                    'name': self._customer_name(order.user),
                    'phone': self._normalize_phone(order.phone)
                },
                'phone': self._normalize_phone(order.phone),
                'deliveryPoint': delivery_point,
                'items': items
            }
        }
        
        # Вся информация об оплате и доставке теперь уходит только в текст комментария
        if order.comment:
            order_data['order']['comment'] = order.comment
        
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
