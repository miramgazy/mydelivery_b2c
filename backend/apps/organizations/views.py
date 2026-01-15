from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Organization, Terminal, Street, PaymentType
from .serializers import (
    OrganizationSerializer, TerminalSerializer,
    StreetSerializer, PaymentTypeSerializer,
    ExternalMenuSerializer
)
from apps.iiko_integration.client import IikoClient, IikoAPIException
from apps.iiko_integration.services import MenuSyncService


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления организациями"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'city']
    search_fields = ['org_name']

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
