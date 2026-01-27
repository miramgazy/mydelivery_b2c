from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
import re
from .models import User, Role, DeliveryAddress, BillingPhone
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, DeliveryAddressSerializer, BillingPhoneSerializer,
    TelegramAuthSerializer
)
from .telegram_auth import validate_telegram_init_data, TelegramAuthException
from core.permissions import IsSuperAdmin, IsOrgAdmin, IsOwner


import logging

logger = logging.getLogger(__name__)

MAX_DELIVERY_ADDRESSES_PER_USER = 3
MAX_BILLING_PHONES_PER_USER = 5

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
            # Валидируем initData (теперь возвращает user_data и organization)
            user_data, organization = validate_telegram_init_data(init_data)
            telegram_id = user_data.get('id')
            logger.info(f"Validated Telegram user: {telegram_id}, organization: {organization.org_name if organization else 'None'}")
            
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
                
                # Обновляем данные и привязываем к организации, если она найдена
                user.first_name = user_data.get('first_name', user.first_name)
                user.last_name = user_data.get('last_name', user.last_name)
                user.telegram_username = user_data.get('username', user.telegram_username)
                
                # Если организация найдена и у пользователя её нет - привязываем
                if organization and not user.organization:
                    user.organization = organization
                    logger.info(f"Attached user {user.id} to organization {organization.org_name}")
                
                user.save(update_fields=['first_name', 'last_name', 'telegram_username', 'organization'])
                
            except User.DoesNotExist:
                # B2C: Автоматически создаем пользователя
                logger.info(f"User not found for telegram_id {telegram_id}. Creating new B2C user.")
                
                # Получаем роль "Клиент"
                from apps.users.models import Role
                try:
                    customer_role = Role.objects.get(role_name=Role.CUSTOMER)
                except Role.DoesNotExist:
                    logger.error("Customer role not found")
                    return Response(
                        {
                            'error': 'Ошибка системы',
                            'message': 'Роль клиента не найдена в системе.'
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Создаем нового пользователя с привязкой к организации
                user = User.objects.create(
                    telegram_id=telegram_id,
                    username=f"tg_{telegram_id}",
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    telegram_username=user_data.get('username', ''),
                    role=customer_role,
                    organization=organization,  # Привязываем к организации
                    is_active=True
                )
                logger.info(f"Created new B2C user: {user.id} with organization: {organization.org_name if organization else 'None'}")
            
            if not user.is_active:
                logger.warning(f"User {user.id} is blocked")
                return Response(
                    {'error': 'Пользователь заблокирован'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            
            # Загружаем пользователя для полного ответа (адреса + терминалы + billing_phones)
            user_with_addresses = User.objects.select_related('role', 'organization').prefetch_related('addresses', 'terminals', 'billing_phones').get(id=user.id)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user_with_addresses).data
            })
            
        except TelegramAuthException as e:
            logger.error(f"Telegram auth exception: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class TelegramWebhookView(viewsets.ViewSet):
    """
    Webhook для обработки апдейтов Telegram-бота (в частности, contact с номером телефона).

    Важно: URL вебхука содержит bot_token, чтобы отличать ботов и защищать endpoint.
    """
    permission_classes = [permissions.AllowAny]

    def webhook(self, request, bot_token=None):
        # Validate bot token - всегда ищем в Organization (multi-bot support)
        if not bot_token:
            return Response({'detail': 'bot_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем организацию по bot_token в базе данных
        from apps.organizations.models import Organization
        organization = Organization.objects.filter(bot_token=bot_token, is_active=True).first()
        if not organization:
            logger.warning(f"Webhook called with unknown bot_token: {bot_token[:10]}... (organization not found)")
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        update = request.data or {}
        message = update.get('message') or update.get('edited_message') or {}
        contact = message.get('contact') or {}

        phone_number = contact.get('phone_number')
        telegram_id = (
            (contact.get('user_id')) or
            (message.get('from') or {}).get('id')
        )

        if not phone_number or not telegram_id:
            # Not a contact update; acknowledge to prevent Telegram retries
            return Response({'ok': True})

        # Normalize phone to "+<digits>"
        phone_number = re.sub(r'[^\d+]', '', str(phone_number))
        digits = re.sub(r'\D', '', phone_number)
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        if not digits.startswith('7'):
            # In our app we store KZ/RU format +7...
            digits = '7' + digits
        phone_number = f"+{digits}"

        user = User.objects.filter(telegram_id=int(telegram_id)).first()
        if not user:
            return Response({'ok': True})

        # Optionally attach organization if this webhook belongs to org bot
        attach_org = bool(organization and not user.organization)
        if attach_org:
            user.organization = organization

        user.phone = phone_number
        user.save(update_fields=['phone', 'organization'] if attach_org else ['phone'])

        logger.info("Saved phone from Telegram contact for user=%s telegram_id=%s", user.id, telegram_id)
        return Response({'ok': True})


class ClientLogView(viewsets.ViewSet):
    """
    Принимает клиентские ошибки/логи из Telegram WebView, чтобы дебажить случаи "белого экрана".
    """
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def log(self, request):
        payload = request.data or {}
        # Логируем в общий лог контейнера
        logger.error("CLIENT_LOG: %s", payload)
        return Response({"ok": True})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""
    queryset = User.objects.select_related('role', 'organization').prefetch_related('addresses', 'billing_phones').all().order_by('-created_at')
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
        logger.info(f"check_access called for telegram_id: {telegram_id}")
        
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
            user = User.objects.get(telegram_id=telegram_id)
            logger.info(f"Found user in check_access: {user.id}, active: {user.is_active}")
            
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
            logger.info(f"User not found in check_access for ID: {telegram_id}")
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
            # Загружаем пользователя с адресами и связанными данными
            user = User.objects.select_related('role', 'organization').prefetch_related('addresses', 'billing_phones').get(id=user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # После обновления загружаем полные данные
            user = User.objects.select_related('role', 'organization').prefetch_related('addresses', 'billing_phones').get(id=user.id)
            return Response(UserSerializer(user).data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='telegram-contact')
    def telegram_contact(self, request):
        """
        Принимает телефон из Telegram-бота (после request_contact/requestContact) и сохраняет его в профиле.

        Ожидает:
        - headers: X-Telegram-Contact-Secret = TELEGRAM_CONTACT_SECRET
        - body: { "telegram_id": <int|string>, "phone": "<string>" }
        """
        secret = request.headers.get('X-Telegram-Contact-Secret', '')
        expected = getattr(settings, 'TELEGRAM_CONTACT_SECRET', '') or ''
        if not expected or secret != expected:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        telegram_id = request.data.get('telegram_id')
        phone = (request.data.get('phone') or '').strip()

        if not telegram_id or not phone:
            return Response(
                {'detail': 'telegram_id и phone обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Нормализуем телефон (оставляем + и цифры)
        phone = re.sub(r'[^\d+]', '', phone)

        user = User.objects.filter(telegram_id=str(telegram_id)).first()
        if not user:
            user = User.objects.filter(telegram_id=int(telegram_id)).first() if str(telegram_id).isdigit() else None
        if not user:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.phone = phone
        user.save(update_fields=['phone'])

        return Response({'ok': True, 'user_id': user.id, 'phone': user.phone})
    
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
        return self.queryset.filter(user=self.request.user).order_by('-is_default', '-updated_at')
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание адреса:
        - Лимит: не более 3 адресов на пользователя
        - Если is_default=True -> снимаем флаг с остальных адресов
        """
        user = self.request.user

        # Блокируем строку пользователя, чтобы сериализовать конкурирующие создания адресов
        User.objects.select_for_update().filter(id=user.id).exists()

        existing_count = DeliveryAddress.objects.filter(user=user).count()
        if existing_count >= MAX_DELIVERY_ADDRESSES_PER_USER:
            raise ValidationError({'detail': f'Можно сохранить не более {MAX_DELIVERY_ADDRESSES_PER_USER} адресов доставки'})

        address = serializer.save(user=user)

        # Если это первый адрес — сделаем его основным (на всякий случай)
        if existing_count == 0 and not address.is_default:
            address.is_default = True
            address.save(update_fields=['is_default'])

        if address.is_default:
            DeliveryAddress.objects.filter(user=user).exclude(id=address.id).update(is_default=False)

        return address

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Обновление адреса:
        - Если is_default=True -> снимаем флаг с остальных адресов пользователя
        """
        user = self.request.user
        address = serializer.save()

        if address.is_default:
            DeliveryAddress.objects.filter(user=user).exclude(id=address.id).update(is_default=False)

        return address

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Запрещаем удаление, если у пользователя остался только один адрес.
        """
        instance = self.get_object()
        remaining = DeliveryAddress.objects.filter(user=request.user).count()
        if remaining <= 1:
            return Response({'detail': 'Нельзя удалить последний адрес доставки'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_destroy(instance)
        except DjangoValidationError as exc:
            # Защита на уровне модели
            msg = ', '.join(exc.messages) if getattr(exc, 'messages', None) else str(exc)
            return Response({'detail': msg}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Установить адрес по умолчанию"""
        address = self.get_object()
        
        # Снимаем флаг с других адресов
        DeliveryAddress.objects.filter(
            user=request.user,
            is_default=True
        ).exclude(id=address.id).update(is_default=False)
        
        # Устанавливаем флаг на текущий
        address.is_default = True
        address.save(update_fields=['is_default'])
        
        return Response(
            DeliveryAddressSerializer(address).data
        )


class BillingPhoneViewSet(viewsets.ModelViewSet):
    """ViewSet для управления дополнительными номерами телефонов (Kaspi и др.)"""
    queryset = BillingPhone.objects.select_related('user').all()
    serializer_class = BillingPhoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свои номера"""
        return self.queryset.filter(user=self.request.user).order_by('-is_default', '-updated_at')

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание номера:
        - Лимит: не более 5 номеров на пользователя
        - Если is_default=True -> снимаем флаг с остальных номеров
        - Если это первый номер, делаем его основным
        """
        user = self.request.user

        BillingPhone.objects.select_for_update().filter(user=user).exists()

        existing_count = BillingPhone.objects.filter(user=user).count()
        if existing_count >= MAX_BILLING_PHONES_PER_USER:
            raise ValidationError({'detail': f'Можно сохранить не более {MAX_BILLING_PHONES_PER_USER} номеров'})

        phone = serializer.validated_data.get('phone', '').strip()
        if not phone:
            raise ValidationError({'phone': 'Номер телефона обязателен'})

        billing_phone = serializer.save(user=user)

        # Если это первый номер — делаем его основным
        if existing_count == 0 and not billing_phone.is_default:
            billing_phone.is_default = True
            billing_phone.save(update_fields=['is_default'])

        if billing_phone.is_default:
            BillingPhone.objects.filter(user=user).exclude(id=billing_phone.id).update(is_default=False)

        return billing_phone

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Обновление номера:
        - Если is_default=True -> снимаем флаг с остальных номеров пользователя
        """
        user = self.request.user
        billing_phone = serializer.save()

        if billing_phone.is_default:
            BillingPhone.objects.filter(user=user).exclude(id=billing_phone.id).update(is_default=False)

        return billing_phone

    def destroy(self, request, *args, **kwargs):
        """
        Удаление номера: без специальных ограничений (всегда можно удалить).
        """
        return super().destroy(request, *args, **kwargs)