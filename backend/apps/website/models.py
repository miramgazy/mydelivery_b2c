"""
Модели для веб-сайта доставки еды.
Стили сайта управляются через таблицу website_styles.
"""
from django.db import models
from apps.organizations.models import Organization


class WebsiteStyles(models.Model):
    """
    Стили веб-сайта организации.
    Управляет цветами, шрифтами и скруглениями через админ-панель.
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='website_styles',
        verbose_name='Организация',
        primary_key=True
    )
    primary_color = models.CharField(
        'Основной цвет (кнопки, акценты)',
        max_length=7,
        default='#FF5733'
    )
    secondary_color = models.CharField(
        'Второстепенный цвет (текст)',
        max_length=7,
        default='#333333'
    )
    background_color = models.CharField(
        'Цвет фона',
        max_length=7,
        default='#FFFFFF'
    )
    font_family = models.CharField(
        'Основной шрифт (Google Fonts)',
        max_length=100,
        default='Inter, sans-serif'
    )
    border_radius = models.IntegerField(
        'Скругление карточек и кнопок (px)',
        default=12
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        db_table = 'website_styles'
        verbose_name = 'Стили сайта'
        verbose_name_plural = 'Стили сайтов'

    def __str__(self):
        return f"Стили: {self.organization.org_name}"
