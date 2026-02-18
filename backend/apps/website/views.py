"""
API для веб-сайта доставки.
Публичные эндпоинты: стили, меню, Telegram Login Widget.
"""
import hashlib
import hmac
import time

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.shortcuts import get_object_or_404

from apps.organizations.models import Organization, Terminal
from apps.products.models import Menu, ProductCategory, Product, StopList
from apps.products.serializers import ProductCategorySerializer, ProductListSerializer, ProductDetailSerializer
from apps.users.models import User, Role
from .models import WebsiteStyles
from .serializers import WebsiteStylesSerializer

import logging

logger = logging.getLogger(__name__)


def _get_org_from_request(request):
    """Получить организацию из query param org"""
    org_id = request.query_params.get('org')
    if not org_id:
        return None, Response(
            {'error': 'Параметр org (UUID организации) обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        org = Organization.objects.get(org_id=org_id, is_active=True)
        return org, None
    except Organization.DoesNotExist:
        return None, Response(
            {'error': 'Организация не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )


def validate_telegram_login_widget(data_dict, bot_token):
    """
    Валидация данных Telegram Login Widget.
    https://core.telegram.org/widgets/login#checking-authorization

    Args:
        data_dict: dict с полями id, first_name, last_name, username, photo_url, auth_date, hash
        bot_token: токен бота

    Returns:
        user_data dict или None при ошибке
    """
    received_hash = data_dict.get('hash')
    if not received_hash:
        return None

    auth_data = {k: v for k, v in data_dict.items() if k != 'hash'}
    data_check_string = '\n'.join(
        f'{k}={v}' for k, v in sorted(auth_data.items())
    )

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if calculated_hash != received_hash:
        logger.warning("Telegram Login Widget: hash mismatch")
        return None

    auth_date = int(auth_data.get('auth_date', 0))
    if time.time() - auth_date > 86400:
        logger.warning("Telegram Login Widget: data expired")
        return None

    return auth_data


class WebsiteStylesView(APIView):
    """
    Публичный API для получения стилей сайта.
    GET /api/website/styles/?org=<organization_uuid>
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org, err = _get_org_from_request(request)
        if err:
            return err

        try:
            styles = WebsiteStyles.objects.get(organization=org)
        except WebsiteStyles.DoesNotExist:
            styles = WebsiteStyles(organization=org)

        serializer = WebsiteStylesSerializer(styles)
        return Response(serializer.data)


class WebsiteMenuView(APIView):
    """
    Публичный API меню для веб-сайта.
    GET /api/website/menu/?org=<organization_uuid>&terminal_id=<optional>
    Возвращает: organization, terminals, categories, products
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org, err = _get_org_from_request(request)
        if err:
            return err

        terminal_id = request.query_params.get('terminal_id')
        terminal = None
        if terminal_id:
            try:
                terminal = Terminal.objects.get(
                    terminal_id=terminal_id,
                    organization=org,
                    is_active=True
                )
            except Terminal.DoesNotExist:
                pass

        active_menu = Menu.objects.filter(
            organization=org,
            is_active=True
        ).first()

        if not active_menu:
            return Response({
                'organization': {
                    'org_id': str(org.org_id),
                    'org_name': org.org_name,
                    'city': org.city,
                    'address': org.address,
                    'phone': org.phone,
                },
                'terminals': [],
                'categories': [],
                'products': [],
            })

        categories = ProductCategory.objects.filter(
            menu=active_menu
        ).order_by('order_index', 'subgroup_name')

        products_qs = Product.objects.filter(
            menu=active_menu,
            organization=org,
            is_available=True
        ).select_related('category').prefetch_related('modifiers').order_by('order_index', 'product_name')

        stop_list_pks = StopList.objects.filter(
            organization=org
        ).values_list('product_id', flat=True)
        if terminal:
            stop_list_pks = StopList.objects.filter(
                organization=org,
                terminal=terminal
            ).values_list('product_id', flat=True)
        products_qs = products_qs.exclude(pk__in=stop_list_pks)

        terminals = [
            {
                'terminal_id': str(t.terminal_id),
                'terminal_group_name': t.terminal_group_name,
                'city_name': t.city.name if t.city else org.city,
            }
            for t in Terminal.objects.filter(organization=org, is_active=True).select_related('city')
        ]

        return Response({
            'organization': {
                'org_id': str(org.org_id),
                'org_name': org.org_name,
                'city': org.city,
                'address': org.address,
                'phone': org.phone,
                'bot_username': org.bot_username,
            },
            'terminals': terminals,
            'categories': ProductCategorySerializer(categories, many=True).data,
            'products': ProductListSerializer(
                products_qs,
                many=True,
                context={'request': request, 'website_public': True}
            ).data,
        })


class TelegramLoginWidgetView(APIView):
    """
    Аутентификация через Telegram Login Widget.
    POST /api/website/telegram-login/
    Body: { "id", "first_name", "last_name", "username", "photo_url", "auth_date", "hash", "org" }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        org_id = request.data.get('org')
        if not org_id:
            return Response(
                {'error': 'Параметр org (UUID организации) обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        org = get_object_or_404(
            Organization.objects.filter(is_active=True, bot_token__isnull=False).exclude(bot_token=''),
            org_id=org_id
        )

        data_dict = {
            'id': str(request.data.get('id', '')),
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'username': request.data.get('username', ''),
            'photo_url': request.data.get('photo_url', ''),
            'auth_date': str(request.data.get('auth_date', '')),
            'hash': request.data.get('hash', ''),
        }

        user_data = validate_telegram_login_widget(data_dict, org.bot_token)
        if not user_data:
            return Response(
                {'error': 'Неверная подпись данных Telegram'},
                status=status.HTTP_400_BAD_REQUEST
            )

        telegram_id = int(user_data.get('id', 0))
        if not telegram_id:
            return Response(
                {'error': 'Telegram ID не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.select_related('role', 'organization').get(
                telegram_id=telegram_id
            )
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.telegram_username = user_data.get('username', user.telegram_username)
            user.organization = org
            user.save(update_fields=['first_name', 'last_name', 'telegram_username', 'organization'])
        except User.DoesNotExist:
            try:
                customer_role = Role.objects.get(role_name=Role.CUSTOMER)
            except Role.DoesNotExist:
                return Response(
                    {'error': 'Роль клиента не найдена'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            username = user_data.get('username') or f'tg_{telegram_id}'
            user = User.objects.create(
                telegram_id=telegram_id,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                telegram_username=user_data.get('username', ''),
                username=username,
                organization=org,
                role=customer_role
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'telegram_id': user.telegram_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.telegram_username,
            }
        })
