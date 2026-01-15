from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .models import User, Role, DeliveryAddress
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, DeliveryAddressSerializer, TelegramAuthSerializer
)
from .telegram_auth import validate_telegram_init_data, TelegramAuthException
from core.permissions import IsSuperAdmin, IsOrgAdmin, IsOwner


import logging

logger = logging.getLogger(__name__)

class TelegramAuthView(viewsets.ViewSet):
    """Аутентификация через Telegram Mini App"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Аутентификация пользователя через Telegram initData
        """
        logger.info("Received Telegram login request")
        logger.debug(f"Request data keys: {list(request.data.keys())}")
        
        serializer = TelegramAuthSerializer(data=request.data)
        if not serializer.is_valid():
             logger.error(f"Serializer validation failed: {serializer.errors}")
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        init_data = serializer.validated_data['initData']
        
        try:
            # Валидируем initData
            user_data = validate_telegram_init_data(init_data)
            telegram_id = user_data.get('id')
            logger.info(f"Validated Telegram user: {telegram_id}")
            
            if not telegram_id:
                logger.error("No telegram_id found in validated data")
                return Response(
                    {'error': 'Telegram ID не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем или создаем пользователя
            try:
                user = User.objects.select_related('role', 'organization').get(
                    telegram_id=telegram_id
                )
                logger.info(f"Found existing user: {user.id}")
                
                # Обновляем данные
                user.first_name = user_data.get('first_name', user.first_name)
                user.last_name = user_data.get('last_name', user.last_name)
                user.telegram_username = user_data.get('username', user.telegram_username)
                user.save(update_fields=['first_name', 'last_name', 'telegram_username'])
                
            except User.DoesNotExist:
                logger.info(f"User not found for telegram_id {telegram_id}, creating new customer")
                # Создаем нового клиента
                customer_role = Role.objects.get(role_name=Role.CUSTOMER)
                user = User.objects.create(
                    telegram_id=telegram_id,
                    first_name=user_data.get('first_name', 'User'),
                    last_name=user_data.get('last_name'),
                    telegram_username=user_data.get('username'),
                    role=customer_role
                )
                logger.info(f"Created new user: {user.id}")
            
            if not user.is_active:
                logger.warning(f"User {user.id} is blocked")
                return Response(
                    {'error': 'Пользователь заблокирован'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
            
        except TelegramAuthException as e:
            logger.error(f"Telegram auth exception: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""
    queryset = User.objects.select_related('role', 'organization').all().order_by('-created_at')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'username', 'phone', 'email']
    filterset_fields = ['role', 'organization', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Права доступа в зависимости от действия"""
        if self.action == 'check_access':
            # Проверка доступа доступна всем
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            # Создавать могут только админы
            permission_classes = [IsSuperAdmin | IsOrgAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактировать и удалять могут админы
            permission_classes = [IsSuperAdmin | IsOrgAdmin]
        elif self.action == 'me':
            # Свои данные может получить любой авторизованный
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Просмотр списка - только админы
            permission_classes = [IsSuperAdmin | IsOrgAdmin]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Фильтрация пользователей в зависимости от роли"""
        user = self.request.user
        
        if user.is_superadmin:
            # Суперадмин видит всех
            return self.queryset
        elif user.is_org_admin:
            # Админ организации видит только пользователей своей организации
            return self.queryset.filter(organization=user.organization)
        else:
            # Обычный пользователь видит только себя
            return self.queryset.filter(id=user.id)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def check_access(self, request):
        """Проверка доступа пользователя по Telegram ID"""
        telegram_id = request.data.get('telegram_id')
        
        if not telegram_id:
            return Response(
                {
                    'has_access': False,
                    'message': 'Telegram ID не предоставлен',
                    'reason': 'invalid_request'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            print(f"DEBUG: check_access for telegram_id={telegram_id} (type={type(telegram_id)})")
            user = User.objects.get(telegram_id=telegram_id)
            print(f"DEBUG: Found user {user.id}, is_active={user.is_active}")
            
            if not user.is_active:
                return Response({
                    'has_access': False,
                    'message': 'Ваш аккаунт заблокирован. Обратитесь к администратору.',
                    'reason': 'blocked',
                    'telegram_id': telegram_id
                })
            
            return Response({
                'has_access': True,
                'message': 'Доступ разрешен',
                'user_exists': True
            })
            
        except User.DoesNotExist:
            return Response({
                'has_access': False,
                'message': 'Вы не зарегистрированы в системе. Обратитесь к администратору для получения доступа.',
                'reason': 'not_found',
                'telegram_id': telegram_id
            })
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Получение/обновление данных текущего пользователя"""
        user = request.user
        
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(user).data)
    
    def create(self, request, *args, **kwargs):
        """Создание пользователя"""
        user = request.user
        
        # Проверяем права создания
        if user.is_org_admin:
            # Админ организации может создавать только пользователей своей организации
            data = request.data.copy()
            data['organization'] = str(user.organization.org_id)
            serializer = self.get_serializer(data=data)
        else:
            serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            UserSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ролей (только чтение)"""
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """ViewSet для адресов доставки"""
    queryset = DeliveryAddress.objects.select_related('user', 'street').all()
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Пользователь видит только свои адреса"""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Автоматическое привязывание к текущему пользователю"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Установить адрес по умолчанию"""
        address = self.get_object()
        
        # Снимаем флаг с других адресов
        DeliveryAddress.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Устанавливаем флаг на текущий
        address.is_default = True
        address.save(update_fields=['is_default'])
        
        return Response(
            DeliveryAddressSerializer(address).data
        )