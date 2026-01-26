"""
Кастомные views для JWT токенов
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from .jwt_serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомный view для получения JWT токенов
    Использует CustomTokenObtainPairSerializer
    """
    serializer_class = CustomTokenObtainPairSerializer
