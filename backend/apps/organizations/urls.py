from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, TerminalViewSet, 
    StreetViewSet, PaymentTypeViewSet, CityViewSet
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'terminals', TerminalViewSet)
router.register(r'streets', StreetViewSet)
router.register(r'payment-types', PaymentTypeViewSet)
router.register(r'cities', CityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]