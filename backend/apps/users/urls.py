from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RoleViewSet, 
    DeliveryAddressViewSet, TelegramAuthView, ClientLogView, TelegramWebhookView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'addresses', DeliveryAddressViewSet)

urlpatterns = [
    path('auth/telegram/', TelegramAuthView.as_view({'post': 'login'}), name='telegram-auth'),
    path('telegram/webhook/<path:bot_token>/', TelegramWebhookView.as_view({'post': 'webhook'}), name='telegram-webhook'),
    path('client-log/', ClientLogView.as_view({'post': 'log'}), name='client-log'),
    path('', include(router.urls)),
]
