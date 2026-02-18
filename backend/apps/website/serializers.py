from rest_framework import serializers
from .models import WebsiteStyles


class WebsiteStylesSerializer(serializers.ModelSerializer):
    """Сериализатор для стилей сайта (публичный API)"""

    class Meta:
        model = WebsiteStyles
        fields = [
            'primary_color', 'secondary_color', 'background_color',
            'font_family', 'border_radius'
        ]
