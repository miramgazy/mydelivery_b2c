"""
Кастомные сериализаторы для JWT токенов
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения JWT токенов
    Поддерживает авторизацию по username или email
    """
    username_field = 'username'
    
    def validate(self, attrs):
        """
        Валидация и получение токенов
        """
        # Получаем username и password
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError({
                'detail': 'Необходимо указать username и password'
            })
        
        # Пытаемся найти пользователя по username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Если не найден по username, пробуем по email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'detail': 'Пользователь с таким username/email не найден'
                })
        
        # Проверяем, активен ли пользователь
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'Пользователь заблокирован'
            })
        
        # Проверяем, есть ли у пользователя пароль
        if not user.has_usable_password():
            raise serializers.ValidationError({
                'detail': 'У этого пользователя не установлен пароль. Используйте авторизацию через Telegram или обратитесь к администратору.'
            })
        
        # Проверяем пароль
        if not user.check_password(password):
            raise serializers.ValidationError({
                'detail': 'Неверный пароль'
            })
        
        # Создаем refresh токен
        refresh = self.get_token(user)
        
        # Добавляем данные пользователя в ответ
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        """
        Получение токена для пользователя
        """
        token = super().get_token(user)
        
        # Добавляем дополнительные данные в токен (опционально)
        token['user_id'] = str(user.id)
        token['username'] = user.username
        if user.role:
            token['role'] = user.role.role_name
        
        return token
