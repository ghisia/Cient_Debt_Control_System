from rest_framework import serializers
from .models import Debt

class DebtSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source='client.name',
        read_only=True
    )

    class Meta:
        model = Debt
        fields = [
            'id',
            'client',
            'client_name',
            'amount',
            'description',
            'date',
            'deadline',
            'status',
        ]
