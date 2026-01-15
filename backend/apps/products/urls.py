from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuViewSet, ProductCategoryViewSet, 
    ProductViewSet, ModifierViewSet, StopListViewSet
)

router = DefaultRouter()
router.register(r'menus', MenuViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'modifiers', ModifierViewSet)
router.register(r'stop-list', StopListViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
