from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import transaction
from .models import Order, OrderItem, OrderItemModifier
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer
)
from .services import OrderService
from core.permissions import IsSuperAdmin, IsOrgAdmin, IsOwner


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для заказов"""
    queryset = Order.objects.select_related(
        'user', 'organization', 'delivery_address', 'payment_type'
    ).prefetch_related('items__modifiers')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'organization']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer
    
    def get_permissions(self):
        """Права доступа"""
        if self.action == 'create':
            # Создавать могут все авторизованные
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактировать могут только админы
            permission_classes = [IsSuperAdmin | IsOrgAdmin]
        else:
            # Просмотр - авторизованные
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Фильтрация заказов в зависимости от роли"""
        user = self.request.user
        queryset = self.queryset
        
        if user.is_superadmin:
            # Суперадмин видит все заказы
            return queryset
        elif user.is_org_admin:
            # Админ организации видит заказы своей организации
            return queryset.filter(organization=user.organization)
        else:
            # Клиент видит только свои заказы
            return queryset.filter(user=user)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Создание заказа
        
        1. Валидация данных
        2. Создание заказа в БД
        3. Отправка в iiko
        4. Обновление статуса
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Проверяем что у пользователя есть организация
        if not request.user.organization:
            return Response(
                {'error': 'Пользователь не привязан к организации'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Создаем заказ через сервис
            order_service = OrderService()
            order = order_service.create_order(
                user=request.user,
                organization=request.user.organization,
                validated_data=serializer.validated_data
            )
            
            # Отправляем в iiko
            success = order_service.send_to_iiko(order)
            
            # Возвращаем созданный заказ
            response_serializer = OrderDetailSerializer(order)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Логируем ошибку
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка создания заказа: {e}', exc_info=True)
            
            return Response(
                {'error': f'Не удалось создать заказ: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Получение актуального статуса заказа из iiko
        """
        order = self.get_object()
        
        # Rate limit check (optional, but requested for the UI)
        # We can implement a simple check based on updated_at or a dedicated field
        import datetime
        from django.utils import timezone
        
        # If user is not admin, we might want to restrict frequency
        if not (request.user.is_superadmin or request.user.is_org_admin):
            if order.updated_at and (timezone.now() - order.updated_at).total_seconds() < 30:
                 return Response({
                    'status': order.status,
                    'message': 'Запрос слишком часто, попробуйте позже',
                    'order': OrderDetailSerializer(order).data
                })

        try:
            order_service = OrderService()
            
            # 1. Если заказ в процессе создания (нет iiko_order_id, но есть correlation_id)
            if order.correlation_id and (order.status == 'InProgress' or not order.iiko_order_id):
                status_data = order_service.update_order_creation_status(order)
            
            # 2. Если уже есть iiko_order_id, запрашиваем детали доставки
            elif order.iiko_order_id:
                status_data = order_service.get_order_details_and_update(order)
            
            else:
                return Response({
                    'status': order.status,
                    'message': 'Заказ еще не отправлен в iiko',
                    'order': OrderDetailSerializer(order).data
                })
            
            return Response({
                'status': order.status,
                'iiko_status': status_data,
                'order': OrderDetailSerializer(order).data
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Ошибка обновления статуса: {e}')
            return Response(
                {'error': f'Не удалось получить статус: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отмена заказа
        """
        order = self.get_object()
        
        # Проверяем права
        if not (request.user.is_superadmin or 
                request.user.is_org_admin or 
                order.user == request.user):
            return Response(
                {'error': 'Недостаточно прав для отмены заказа'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем возможность отмены
        if order.status in [Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]:
            return Response(
                {'error': f'Невозможно отменить заказ в статусе "{order.get_status_display()}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Обновляем статус
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status', 'updated_at'])
        
        # TODO: Отправить отмену в iiko если заказ уже там
        
        return Response(
            OrderDetailSerializer(order).data
        )
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        Получение заказов текущего пользователя
        """
        orders = self.get_queryset().filter(user=request.user)
        
        # Применяем фильтры
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Пагинация
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Статистика по заказам (только для админов)
        """
        if not (request.user.is_superadmin or request.user.is_org_admin):
            return Response(
                {'error': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        from django.db.models import Count, Sum, Avg
        
        stats = queryset.aggregate(
            total_orders=Count('order_id'),
            total_amount=Sum('total_amount'),
            average_amount=Avg('total_amount'),
            pending_count=Count('order_id', filter=Q(status=Order.STATUS_PENDING)),
            confirmed_count=Count('order_id', filter=Q(status=Order.STATUS_CONFIRMED)),
            completed_count=Count('order_id', filter=Q(status=Order.STATUS_COMPLETED)),
            cancelled_count=Count('order_id', filter=Q(status=Order.STATUS_CANCELLED)),
        )
        
        return Response(stats)