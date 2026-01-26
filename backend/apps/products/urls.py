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

# Stop-list регистрируем отдельным роутером, чтобы избежать конфликта с /api/products/{pk}/
stop_list_router = DefaultRouter()
stop_list_router.register(r'stop-list', StopListViewSet, basename='stoplist')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(stop_list_router.urls)),
]
