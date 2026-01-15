from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, RoleViewSet, 
    DeliveryAddressViewSet, TelegramAuthView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'addresses', DeliveryAddressViewSet)

urlpatterns = [
    path('auth/telegram/', TelegramAuthView.as_view({'post': 'login'}), name='telegram-auth'),
    path('', include(router.urls)),
]
