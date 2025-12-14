from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source='client.name',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'client',
            'client_name',
            'debt',
            'amount',
            'date',
        ]
