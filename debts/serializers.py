from rest_framework import serializers
from .models import Debt
from clients.serializers import ClientSerializer


class DebtSerializer(serializers.ModelSerializer):
    """Serializer for Debt model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    amount_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Debt
        fields = [
            'id', 'client', 'client_name', 'client_email',
            'amount', 'description', 'date', 'deadline',
            'status', 'amount_paid', 'remaining_balance',
            'days_until_deadline', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_amount_paid(self, obj):
        """Get total amount paid towards this debt."""
        return float(obj.get_amount_paid())
    
    def get_remaining_balance(self, obj):
        """Get remaining balance for this debt."""
        return float(obj.get_remaining_balance())
    
    def get_days_until_deadline(self, obj):
        """Get days remaining until deadline."""
        return obj.days_until_deadline()
    
    def get_is_overdue(self, obj):
        """Check if debt is overdue."""
        return obj.is_overdue()
    
    def validate(self, data):
        """Validate debt data."""
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        
        if data.get('deadline') and data.get('date'):
            if data['deadline'] < data['date']:
                raise serializers.ValidationError(
                    "Deadline cannot be before the debt date."
                )
        
        return data


class DebtDetailSerializer(DebtSerializer):
    """Detailed serializer for Debt model with client and payment info."""
    
    client = ClientSerializer(read_only=True)
    payments = serializers.SerializerMethodField()
    
    class Meta(DebtSerializer.Meta):
        fields = DebtSerializer.Meta.fields + ['payments']
    
    def get_payments(self, obj):
        """Get all payments for this debt."""
        from payments.serializers import PaymentSerializer
        return PaymentSerializer(obj.payments.all(), many=True).data
