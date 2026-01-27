from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuViewSet, ProductCategoryViewSet, 
    ProductViewSet, ModifierViewSet, StopListViewSet,
    FastMenuGroupViewSet, FastMenuGroupPublicViewSet
)

router = DefaultRouter()
router.register(r'menus', MenuViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'modifiers', ModifierViewSet)

# Stop-list регистрируем отдельным роутером, чтобы избежать конфликта с /api/products/{pk}/
stop_list_router = DefaultRouter()
stop_list_router.register(r'stop-list', StopListViewSet, basename='stoplist')

# Fast Menu роутеры
fast_menu_router = DefaultRouter()
fast_menu_router.register(r'fast-menu-groups', FastMenuGroupViewSet, basename='fastmenugroup')

fast_menu_public_router = DefaultRouter()
fast_menu_public_router.register(r'fast-menu', FastMenuGroupPublicViewSet, basename='fastmenugrouppublic')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(stop_list_router.urls)),
    path('', include(fast_menu_router.urls)),
    path('', include(fast_menu_public_router.urls)),
]
