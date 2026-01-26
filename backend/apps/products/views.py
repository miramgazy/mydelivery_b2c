from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from .models import Menu, ProductCategory, Product, Modifier, StopList
from .serializers import (
    MenuSerializer, ProductCategorySerializer,
    ProductListSerializer, ProductDetailSerializer,
    ModifierSerializer, StopListSerializer
)
from core.permissions import IsSuperAdmin, IsOrgAdmin


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для меню"""
    queryset = Menu.objects.select_related('organization').filter(is_active=True)
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'is_active']
    search_fields = ['menu_name']
    
    def get_queryset(self):
        """Фильтрация меню по организации пользователя"""
        user = self.request.user
        queryset = self.queryset
        
        if not user.is_superadmin and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset


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
        """Фильтрация категорий по организации меню"""
        user = self.request.user
        queryset = self.queryset
        
        if not user.is_superadmin and user.organization:
            queryset = queryset.filter(menu__organization=user.organization)
        
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
                
                stop_list_products = stop_list_query.values_list('product_id', flat=True)
                
                queryset = queryset.exclude(product_id__in=stop_list_products)
        
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