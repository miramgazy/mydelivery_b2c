from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.db import transaction
from .models import Menu, ProductCategory, Product, Modifier, StopList, FastMenuGroup, FastMenuItem
from .serializers import (
    MenuSerializer, ProductCategorySerializer,
    ProductListSerializer, ProductDetailSerializer,
    ModifierSerializer, StopListSerializer,
    FastMenuGroupSerializer, FastMenuGroupPublicSerializer, FastMenuItemSerializer
)
from core.permissions import IsSuperAdmin, IsOrgAdmin


class MenuViewSet(viewsets.ModelViewSet):
    """ViewSet для меню. Список для управления: ?for_management=1 (все меню). PATCH is_active с единственным активным на организацию."""
    queryset = Menu.objects.select_related('organization').all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'menu_id'
    lookup_url_kwarg = 'menu_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'is_active']
    search_fields = ['menu_name']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        base = Menu.objects.select_related('organization')
        if not getattr(user, 'is_superadmin', False) and getattr(user, 'organization', None):
            base = base.filter(organization=user.organization)
        # Для списка: админ с for_management=1 видит все меню, иначе только активные
        if self.request.query_params.get('for_management') == '1' and (getattr(user, 'is_superadmin', False) or getattr(user, 'is_org_admin', False)):
            return base
        # Для update/partial_update/destroy админ или владелец организации видит все меню
        if self.action in ('update', 'partial_update', 'destroy'):
            if getattr(user, 'is_superadmin', False) or getattr(user, 'is_org_admin', False):
                return base
            if getattr(user, 'organization', None):
                return base
        return base.filter(is_active=True)

    def get_permissions(self):
        # partial_update (toggle is_active) — только IsAuthenticated; объект проверяется в check_object_permissions
        if self.action == 'partial_update':
            return [permissions.IsAuthenticated()]
        if self.action in ('update', 'destroy', 'create'):
            return [permissions.IsAuthenticated(), IsSuperAdmin() | IsOrgAdmin()]
        return [permissions.IsAuthenticated()]

    def check_object_permissions(self, request, obj):
        """Для PATCH: разрешить только если меню принадлежит организации пользователя или пользователь админ."""
        if request.method == 'PATCH':
            user = request.user
            if getattr(user, 'is_superadmin', False) or getattr(user, 'is_org_admin', False):
                super().check_object_permissions(request, obj)
                return
            if getattr(user, 'organization', None) and getattr(obj, 'organization_id', None) == user.organization_id:
                return
            raise PermissionDenied('Меню не принадлежит вашей организации.')
        super().check_object_permissions(request, obj)

    def perform_update(self, serializer):
        instance = serializer.save()
        if getattr(instance, 'is_active', False):
            Menu.objects.filter(organization=instance.organization).exclude(pk=instance.pk).update(is_active=False)


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для категорий продуктов"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['menu']
    ordering_fields = ['order_index', 'subgroup_name']
    ordering = ['order_index', 'subgroup_name']
    pagination_class = None
    
    def get_queryset(self):
        """Фильтрация категорий по организации меню; для клиентов — только активное меню"""
        user = self.request.user
        queryset = self.queryset
        if not user.is_superadmin and user.organization:
            queryset = queryset.filter(menu__organization=user.organization)
        if getattr(user, 'is_customer', False):
            queryset = queryset.filter(menu__is_active=True)
        return queryset


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для продуктов"""
    queryset = Product.objects.select_related(
        'menu', 'organization', 'category'
    ).prefetch_related('modifiers')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['menu', 'category', 'is_available', 'organization']
    search_fields = ['product_name', 'description']
    ordering_fields = ['order_index', 'product_name', 'price']
    ordering = ['order_index', 'product_name']
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """
        Фильтрация продуктов:
        - Только доступные продукты для клиентов
        - Исключаем продукты из стоп-листа (с учетом terminal_id если указан)
        - Фильтруем по организации
        """
        user = self.request.user
        queryset = self.queryset
        
        # Фильтрация по организации
        if not user.is_superadmin and user.organization:
            queryset = queryset.filter(organization=user.organization)

        # TMA/клиенты: только продукты из активного меню
        if user.is_customer:
            queryset = queryset.filter(menu__is_active=True)

        # Клиенты видят только доступные продукты
        if user.is_customer:
            queryset = queryset.filter(is_available=True)
            
            # Исключаем продукты из стоп-листа
            if user.organization:
                # Получаем terminal_id из query параметров
                terminal_id = self.request.query_params.get('terminal_id')
                
                stop_list_query = StopList.objects.filter(
                    organization=user.organization
                )
                
                # Если указан terminal_id, фильтруем по нему
                if terminal_id:
                    try:
                        from apps.organizations.models import Terminal
                        terminal = Terminal.objects.get(terminal_id=terminal_id)
                        stop_list_query = stop_list_query.filter(terminal=terminal)
                    except (Terminal.DoesNotExist, ValueError):
                        # Если terminal не найден, используем все стоп-листы организации
                        pass
                
                # stop_list.product_id references Product.pk (Product.id)
                stop_list_product_pks = stop_list_query.values_list('product_id', flat=True)
                queryset = queryset.exclude(pk__in=stop_list_product_pks)
        
        return queryset


class ModifierViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модификаторов"""
    queryset = Modifier.objects.select_related('product')
    serializer_class = ModifierSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    ordering = ['modifier_name', 'price']

    def get_queryset(self):
        """Фильтрация модификаторов по организации пользователя через продукт"""
        user = self.request.user
        queryset = self.queryset
        
        if not user.is_superadmin and getattr(user, 'organization', None):
            queryset = queryset.filter(product__organization=user.organization)
            
        return queryset


class StopListViewSet(viewsets.ModelViewSet):
    """ViewSet для стоп-листа"""
    queryset = StopList.objects.select_related('product', 'organization', 'terminal')
    serializer_class = StopListSerializer
    permission_classes = [IsSuperAdmin | IsOrgAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'product', 'terminal', 'is_auto_added']
    search_fields = ['product_name', 'reason']
    pagination_class = None  # Отключаем пагинацию для стоп-листа
    
    def get_queryset(self):
        """Админ организации видит только стоп-лист своей организации"""
        import logging
        logger = logging.getLogger(__name__)
        
        user = self.request.user
        queryset = self.queryset
        
        if user.is_org_admin:
            # Используем ту же логику, что и в /api/organizations/me/
            organization = None
            
            # Сначала проверяем прямую привязку к организации
            if hasattr(user, 'organization') and user.organization:
                organization = user.organization
            else:
                # Если организации нет, пытаемся получить через терминалы пользователя
                try:
                    user_terminals = user.terminals.all()
                    if user_terminals.exists():
                        first_terminal = user_terminals.first()
                        if first_terminal and first_terminal.organization:
                            organization = first_terminal.organization
                except Exception as e:
                    logger.warning(f"Error getting organization from terminals: {e}", exc_info=True)
            
            # Если организация все еще не найдена, берем первую активную (как в get_current_organization)
            if not organization:
                try:
                    from apps.organizations.models import Organization
                    organization = Organization.objects.filter(is_active=True).first()
                except Exception as e:
                    logger.warning(f"Error getting first active organization: {e}", exc_info=True)
            
            if organization:
                queryset = queryset.filter(organization=organization)
            else:
                # Если организация не определена, возвращаем пустой queryset
                queryset = queryset.none()
                logger.warning("No organization found for user, returning empty queryset")
        elif user.is_superadmin:
            # Суперадмин видит все
            pass
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматическое заполнение product_name при создании"""
        product = serializer.validated_data.get('product')
        if product:
            serializer.save(product_name=product.product_name)


class FastMenuGroupViewSet(viewsets.ModelViewSet):
    """ViewSet для групп быстрого меню (админка)"""
    queryset = FastMenuGroup.objects.select_related('organization').prefetch_related(
        'items__product', 'items__product__category'
    )
    serializer_class = FastMenuGroupSerializer
    permission_classes = [IsSuperAdmin | IsOrgAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'is_active']
    search_fields = ['name']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']
    
    def get_queryset(self):
        """Фильтрация групп по организации пользователя"""
        user = self.request.user
        queryset = self.queryset
        
        if user.is_org_admin:
            # Используем ту же логику, что и в StopListViewSet
            organization = None
            
            if hasattr(user, 'organization') and user.organization:
                organization = user.organization
            else:
                try:
                    user_terminals = user.terminals.all()
                    if user_terminals.exists():
                        first_terminal = user_terminals.first()
                        if first_terminal and first_terminal.organization:
                            organization = first_terminal.organization
                except Exception:
                    pass
            
            if not organization:
                try:
                    from apps.organizations.models import Organization
                    organization = Organization.objects.filter(is_active=True).first()
                except Exception:
                    pass
            
            if organization:
                queryset = queryset.filter(organization=organization)
            else:
                queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Автоматическое заполнение organization при создании"""
        user = self.request.user
        organization = serializer.validated_data.get('organization')
        
        if not organization and user.is_org_admin:
            # Получаем организацию пользователя
            if hasattr(user, 'organization') and user.organization:
                organization = user.organization
            else:
                try:
                    user_terminals = user.terminals.all()
                    if user_terminals.exists():
                        first_terminal = user_terminals.first()
                        if first_terminal and first_terminal.organization:
                            organization = first_terminal.organization
                except Exception:
                    pass
            
            if not organization:
                try:
                    from apps.organizations.models import Organization
                    organization = Organization.objects.filter(is_active=True).first()
                except Exception:
                    pass
        
        if organization:
            serializer.save(organization=organization)
        else:
            serializer.save()
    
    @action(detail=True, methods=['put', 'patch'], url_path='items')
    def update_items(self, request, pk=None):
        """Обновление списка товаров в группе"""
        group = self.get_object()
        product_ids = request.data.get('product_ids', [])
        
        if not isinstance(product_ids, list):
            return Response(
                {'error': 'product_ids должен быть массивом'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Удаляем все существующие элементы
                group.items.all().delete()
                
                # Товары только из активного меню (product_id не уникален глобально).
                products_qs = Product.objects.filter(
                    product_id__in=product_ids,
                    organization=group.organization,
                    menu__is_active=True,
                )
                products_by_id = {p.product_id: p for p in products_qs}
                items = []
                for order, pid in enumerate(product_ids):
                    product = products_by_id.get(pid)
                    if not product:
                        continue
                    items.append(
                        FastMenuItem(
                            group=group,
                            product=product,
                            order=order
                        )
                    )
                
                FastMenuItem.objects.bulk_create(items)
                
                # Возвращаем обновленную группу
                serializer = self.get_serializer(group)
                return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FastMenuGroupPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для групп быстрого меню (для TMA)"""
    queryset = FastMenuGroup.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'items',
            queryset=FastMenuItem.objects.select_related('product', 'product__category')
                .prefetch_related('product__modifiers')
                .order_by('order')
        )
    )
    serializer_class = FastMenuGroupPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']
    pagination_class = None
    
    def get_queryset(self):
        """Фильтрация групп по организации пользователя"""
        user = self.request.user
        queryset = self.queryset.filter(is_active=True)
        
        if not user.is_superadmin and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset