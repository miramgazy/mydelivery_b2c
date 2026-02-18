from django.urls import path
from .views import WebsiteStylesView, WebsiteMenuView, TelegramLoginWidgetView

urlpatterns = [
    path('styles/', WebsiteStylesView.as_view(), name='website-styles'),
    path('menu/', WebsiteMenuView.as_view(), name='website-menu'),
    path('telegram-login/', TelegramLoginWidgetView.as_view(), name='website-telegram-login'),
]
