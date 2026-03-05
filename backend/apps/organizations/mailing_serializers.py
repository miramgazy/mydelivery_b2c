from django.utils import timezone
from rest_framework import serializers

from apps.organizations.models import MailingTask, MailingStatus, MailingAudienceType


class MailingTaskSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source='organization.org_name',
        read_only=True,
        default=None,
    )

    class Meta:
        model = MailingTask
        fields = [
            'id',
            'organization',
            'organization_name',
            'title',
            'audience_type',
            'message_ru',
            'message_kz',
            'scheduled_at',
            'created_at',
            'updated_at',
            'status',
            'total_recipients',
            'sent_ru',
            'sent_kz',
            'failed_count',
            'unsubscribed_count',
        ]
        read_only_fields = [
            'id',
            'organization',
            'organization_name',
            'created_at',
            'updated_at',
            'total_recipients',
            'sent_ru',
            'sent_kz',
            'failed_count',
            'unsubscribed_count',
        ]

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Нельзя назначить рассылку в прошлом времени.')
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and not instance.is_editable:
            raise serializers.ValidationError('Нельзя редактировать рассылку в этом статусе.')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'organization', None):
            raise serializers.ValidationError('Пользователь не привязан к организации.')
        validated_data['organization'] = user.organization
        validated_data.setdefault('status', MailingStatus.SCHEDULED)
        return super().create(validated_data)

