from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, TerminalViewSet,
    StreetViewSet, PaymentTypeViewSet, CityViewSet, DiscountViewSet,
    MailingTaskViewSet,
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'terminals', TerminalViewSet)
router.register(r'streets', StreetViewSet)
router.register(r'payment-types', PaymentTypeViewSet)
router.register(r'cities', CityViewSet)
router.register(r'discounts', DiscountViewSet)
# Эндпоинты рассылок живут под /api/organizations/mailings/
router.register(r'organizations/mailings', MailingTaskViewSet, basename='mailings')

urlpatterns = [
    path('', include(router.urls)),
]