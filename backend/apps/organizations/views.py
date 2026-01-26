import logging
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

from .models import Organization, Terminal, Street, PaymentType, City
from .serializers import (
    OrganizationSerializer, TerminalSerializer,
    StreetSerializer, PaymentTypeSerializer,
    CitySerializer, ExternalMenuSerializer
)
from apps.iiko_integration.client import IikoClient, IikoAPIException
from apps.iiko_integration.services import MenuSyncService, StopListSyncService


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления организациями"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'city']
    search_fields = ['org_name']

    @action(detail=False, methods=['get'], url_path='by-bot')
    def get_organization_by_bot(self, request):
        """Получить организацию по bot_token или bot_username"""
        bot_token = request.query_params.get('bot_token')
        bot_username = request.query_params.get('bot_username')
        
        if not bot_token and not bot_username:
            return Response(
                {'error': 'Необходимо указать bot_token или bot_username'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if bot_token:
                organization = Organization.objects.get(bot_token=bot_token, is_active=True)
            else:
                organization = Organization.objects.get(bot_username=bot_username, is_active=True)
            
            serializer = self.get_serializer(organization)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Organization.MultipleObjectsReturned:
            return Response(
                {'error': 'Найдено несколько организаций с указанными параметрами'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_organization(self, request):
        """Получить организацию текущего пользователя"""
        # Предполагаем, что у пользователя есть связанная организация
        # Можно адаптировать логику в зависимости от вашей модели User
        user = request.user
        
        # Если у вас есть поле organization в модели User
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            # Иначе берем первую активную организацию или создаем
            organization = Organization.objects.filter(is_active=True).first()
            if not organization:
                return Response(
                    {'error': 'Организация не найдена'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(organization)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='me')
    def update_current_organization(self, request):
        """Обновить организацию текущего пользователя"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
            if not organization:
                return Response(
                    {'error': 'Организация не найдена'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(
            organization, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='terminals')
    def get_terminals(self, request):
        """Получить терминалы организации"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response([])
        
        terminals = Terminal.objects.filter(organization=organization)
        serializer = TerminalSerializer(terminals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='load-terminals')
    def load_terminals(self, request):
        """Загрузить терминалы из iiko"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not organization.api_key or not organization.iiko_organization_id:
            return Response(
                {'error': 'Не настроены iiko_organization_id или api_key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = IikoClient(organization.api_key)
            terminal_groups_data = client.get_terminal_groups([organization.iiko_organization_id])
            
            # Синхронизируем терминалы
            service = MenuSyncService()
            service.sync_terminal_groups(terminal_groups_data, organization)
            
            return Response({
                'message': 'Терминалы успешно загружены из iiko',
                'success': True
            })
        except IikoAPIException as e:
            return Response(
                {'error': f'Ошибка при загрузке терминалов из iiko: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='payment-types')
    def get_payment_types(self, request):
        """Получить типы оплат организации"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response([])
        
        payment_types = PaymentType.objects.filter(organization=organization)
        serializer = PaymentTypeSerializer(payment_types, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='load-payment-types')
    def load_payment_types(self, request):
        """Загрузить типы оплат из iiko"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not organization.api_key or not organization.iiko_organization_id:
            return Response(
                {'error': 'Не настроены iiko_organization_id или api_key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = IikoClient(organization.api_key)
            payment_types_data = client.get_payment_types([organization.iiko_organization_id])
            
            # Синхронизируем типы оплат
            service = MenuSyncService()
            service.sync_payment_types(organization, payment_types_data)
            
            return Response({
                'message': 'Типы оплат успешно загружены из iiko',
                'success': True
            })
        except IikoAPIException as e:
            return Response(
                {'error': f'Ошибка при загрузке типов оплат из iiko: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='external-menus')
    def get_external_menus(self, request):
        """Получить список внешних меню из iiko"""
        user = request.user
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not organization.api_key or not organization.iiko_organization_id:
            return Response(
                {'error': 'Не настроены iiko_organization_id или api_key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = IikoClient(organization.api_key)
            # Получаем список внешних меню
            response = client.get_external_menus([organization.iiko_organization_id])
            
            # Преобразуем в нужный формат
            external_menus = []
            if 'externalMenus' in response:
                for menu in response['externalMenus']:
                    external_menus.append({
                        'id': menu.get('id'),
                        'external_menu_id': menu.get('id'),
                        'name': menu.get('name', 'Unnamed Menu')
                    })
            
            serializer = ExternalMenuSerializer(external_menus, many=True)
            return Response(serializer.data)
        except IikoAPIException as e:
            return Response(
                {'error': f'Ошибка при получении списка меню из iiko: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='menu-groups')
    def get_menu_groups(self, request):
        """Получить список корневых групп меню (как в админке)"""
        user = request.user
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
            
        if not organization or not organization.api_key:
             return Response({'error': 'Organization not configured'}, status=400)
             
        try:
            client = IikoClient(organization.api_key)
            menu_data = client.get_menu(organization.iiko_organization_id)
            all_groups = menu_data.get('groups', [])
            
            # Логика из admin.py
            children_counts = {}
            for g in all_groups:
                p_id = g.get('parentGroup')
                if p_id:
                    children_counts[p_id] = children_counts.get(p_id, 0) + 1
            
            root_groups = []
            for g in all_groups:
                if not g.get('parentGroup'):
                    # Добавляем инфо о количестве детей
                    g['childrenCount'] = children_counts.get(g['id'], 0)
                    root_groups.append(g)
            
            # Сортируем по имени
            root_groups.sort(key=lambda x: x.get('name', ''))
            
            return Response(root_groups)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='load-menu-groups')
    def load_menu_groups(self, request):
        """Загрузить выбранные группы меню"""
        user = request.user
        # groups_ids = request.data.get('groups', []) # List of strings ID
        # Если groups пусто, но флаг load_all=True, то грузим всё.
        # Но чтобы было "как в админке", принимаем selected_ids
        
        selected_ids = request.data.get('selected_groups', [])
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
            
        if not organization: 
            return Response({'error': 'Org not found'}, status=400)
            
        try:
            client = IikoClient(organization.api_key)
            menu_data = client.get_menu(organization.iiko_organization_id)
            
            service = MenuSyncService()
            if selected_ids:
                service.sync_selected_roots(organization, menu_data, selected_ids)
                msg = f"Загружено {len(selected_ids)} групп"
            else:
                # Если ничего не выбрано, но вызван метод -> возможно sync all?
                # Админка требует выбора. Но для UX сделаем fallback
                service.sync_menu(organization, menu_data)
                msg = "Загружено полное меню"
                
            return Response({'message': msg, 'success': True})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'], url_path='load-menu')
    def load_menu(self, request):
        """Загрузить меню из iiko (конкретное или общее)"""
        user = request.user
        external_menu_id = request.data.get('external_menu_id')
        
        if hasattr(user, 'organization') and user.organization:
            organization = user.organization
        else:
            organization = Organization.objects.filter(is_active=True).first()
        
        if not organization:
            return Response(
                {'error': 'Организация не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not organization.api_key or not organization.iiko_organization_id:
            return Response(
                {'error': 'Не настроены iiko_organization_id или api_key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = IikoClient(organization.api_key)
            
            # Если ID внешнего меню передан - используем его (если метод клиента поддерживает)
            # Если нет - загружаем основную номенклатуру
            # Примечание: get_menu обычно загружает nomenclature без аргументов внешнего меню в текущей реализации,
            # но мы оставим возможность расширения.
            
            # В текущей реализации IikoClient.get_menu принимает organization_id
            # Чтобы загрузить конкретное внешнее меню, возможно понадобится другой метод API,
            # но пока используем стандартный get_menu который тянет всё дерево.
            menu_data = client.get_menu(organization.iiko_organization_id)
            
            # Синхронизируем меню
            service = MenuSyncService()
            service.sync_menu(organization, menu_data)
            
            return Response({
                'message': 'Меню успешно загружено из iiko',
                'success': True
            })
        except IikoAPIException as e:
            return Response(
                {'error': f'Ошибка при загрузке меню из iiko: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Логируем полный трейсбек для отладки
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TerminalViewSet(viewsets.ModelViewSet):
    """ViewSet для управления терминалами"""
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='sync-stop-list')
    def sync_stop_list(self, request, pk=None):
        """Принудительно синхронизировать стоп-лист для терминала"""
        terminal = self.get_object()
        
        if not terminal.organization:
            return Response(
                {'error': 'Терминал должен быть привязан к организации'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        organization = terminal.organization
        
        if not organization.api_key:
            return Response(
                {'error': 'У организации должен быть настроен API ключ iiko'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = StopListSyncService(organization.api_key)
            result = service.sync_terminal_stop_list(terminal)
            
            return Response({
                'message': 'Стоп-лист успешно синхронизирован',
                'success': True,
                'data': result
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IikoAPIException as e:
            return Response(
                {'error': f'Ошибка при синхронизации стоп-листа из iiko: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при синхронизации стоп-листа: {e}", exc_info=True)
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], url_path='delivery-zones')
    def update_delivery_zones(self, request, pk=None):
        """Обновить зоны доставки для терминала"""
        terminal = self.get_object()
        
        delivery_zones = request.data.get('delivery_zones_conditions')
        
        if delivery_zones is None:
            return Response(
                {'error': 'Поле delivery_zones_conditions обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация формата данных
        if not isinstance(delivery_zones, list):
            return Response(
                {'error': 'delivery_zones_conditions должен быть массивом'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация структуры каждой зоны
        for i, zone in enumerate(delivery_zones):
            if not isinstance(zone, dict):
                return Response(
                    {'error': f'Зона #{i+1} должна быть объектом'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверка обязательных полей
            if 'coordinates' not in zone or not zone['coordinates']:
                return Response(
                    {'error': f'В зоне #{i+1} отсутствуют координаты'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(zone['coordinates'], list) or len(zone['coordinates']) < 3:
                return Response(
                    {'error': f'В зоне #{i+1} должно быть минимум 3 точки координат'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Установка значений по умолчанию
            zone.setdefault('name', f'Зона {i+1}')
            zone.setdefault('priority', i+1)
            zone.setdefault('color', '#FF0000')
            zone.setdefault('delivery_type', 'free')
            zone.setdefault('delivery_cost', 0)
        
        try:
            terminal.delivery_zones_conditions = delivery_zones
            terminal.save()
            
            serializer = self.get_serializer(terminal)
            return Response({
                'message': 'Зоны доставки успешно обновлены',
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Ошибка при обновлении зон доставки: {e}", exc_info=True)
            return Response(
                {'error': f'Неожиданная ошибка: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StreetViewSet(viewsets.ModelViewSet):
    """ViewSet для управления улицами"""
    queryset = Street.objects.all()
    serializer_class = StreetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'city', 'is_deleted']
    search_fields = ['street_name']


class PaymentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet для типов оплаты"""
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'is_active', 'payment_type']


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для городов (только чтение)"""
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'is_active']
    search_fields = ['name']
