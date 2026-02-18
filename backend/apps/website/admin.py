from django.contrib import admin
from django import forms
from .models import WebsiteStyles


class WebsiteStylesAdminForm(forms.ModelForm):
    """Форма с виджетом выбора цвета"""
    primary_color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'style': 'width: 60px; height: 30px; padding: 2px; cursor: pointer;'}),
        max_length=7
    )
    secondary_color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'style': 'width: 60px; height: 30px; padding: 2px; cursor: pointer;'}),
        max_length=7
    )
    background_color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color', 'style': 'width: 60px; height: 30px; padding: 2px; cursor: pointer;'}),
        max_length=7
    )

    class Meta:
        model = WebsiteStyles
        fields = '__all__'


@admin.register(WebsiteStyles)
class WebsiteStylesAdmin(admin.ModelAdmin):
    form = WebsiteStylesAdminForm
    list_display = ('organization', 'primary_color', 'font_family', 'border_radius', 'updated_at')
    list_filter = ('organization',)
    search_fields = ('organization__org_name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('organization',)
        }),
        ('Цвета', {
            'fields': ('primary_color', 'secondary_color', 'background_color'),
            'description': 'Выберите цвета для оформления сайта (HEX формат)'
        }),
        ('Типографика', {
            'fields': ('font_family', 'border_radius'),
            'description': 'Шрифт из Google Fonts (например: Inter, Roboto, Open Sans)'
        }),
        (None, {
            'fields': ('created_at', 'updated_at')
        }),
    )
