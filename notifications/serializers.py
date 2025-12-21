from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    debt_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'client', 'client_name', 'debt', 'debt_info',
            'recipient_email', 'vendor_email', 'subject', 'message',
            'scheduled_for', 'sent_at', 'status', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'status', 'error_message', 'created_at']
    
    def get_debt_info(self, obj):
        """Get basic debt information if available."""
        if obj.debt:
            return {
                'id': obj.debt.id,
                'amount': float(obj.debt.amount),
                'deadline': obj.debt.deadline,
                'status': obj.debt.status
            }
        return None


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'client', 'debt', 'recipient_email', 'vendor_email',
            'subject', 'message', 'scheduled_for'
        ]
    
    def validate_scheduled_for(self, value):
        """Ensure scheduled time is in the future."""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value


class NotificationSendSerializer(serializers.Serializer):
    """Serializer for manually sending a notification."""
    
    notification_id = serializers.IntegerField()
    
    def validate_notification_id(self, value):
        """Validate notification exists and is pending."""
        try:
            notification = Notification.objects.get(id=value)
            if notification.status == 'SENT':
                raise serializers.ValidationError(
                    "This notification has already been sent."
                )
        except Notification.DoesNotExist:
            raise serializers.ValidationError(
                "Notification not found."
            )
        return value
