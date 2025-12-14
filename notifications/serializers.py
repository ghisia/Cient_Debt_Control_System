from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source='client.name',
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id',
            'client',
            'client_name',
            'vendor_phone',
            'message',
            'scheduled_for',
            'status',
        ]
