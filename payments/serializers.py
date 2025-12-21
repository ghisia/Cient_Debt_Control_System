from rest_framework import serializers
from .models import Payment
from django.utils import timezone


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    debt_amount = serializers.DecimalField(
        source='debt.amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'id', 'client', 'client_name', 'debt', 'debt_amount',
            'amount', 'date', 'reference_number', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_amount(self, value):
        """Validate payment amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value
    
    def validate(self, data):
        """Validate payment data."""
        # Check if payment exceeds remaining debt balance
        debt = data.get('debt')
        amount = data.get('amount')
        
        if debt and amount:
            remaining = debt.get_remaining_balance()
            if amount > remaining:
                raise serializers.ValidationError(
                    f"Payment amount (${amount}) exceeds remaining debt balance (${remaining})."
                )
        
        # Ensure client matches debt's client
        client = data.get('client')
        if debt and client and client != debt.client:
            raise serializers.ValidationError(
                "Payment client must match the debt's client."
            )
        
        return data
    
    def create(self, validated_data):
        """Create payment and update debt status."""
        payment = super().create(validated_data)
        # The save method in the model will handle debt status update
        return payment


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating payments."""
    
    class Meta:
        model = Payment
        fields = ['debt', 'amount', 'date', 'reference_number', 'notes']
    
    def validate_amount(self, value):
        """Validate payment amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value
    
    def validate(self, data):
        """Validate payment data."""
        debt = data.get('debt')
        amount = data.get('amount')
        
        if debt and amount:
            remaining = debt.get_remaining_balance()
            if amount > remaining:
                raise serializers.ValidationError(
                    f"Payment amount (${amount}) exceeds remaining debt balance (${remaining})."
                )
        
        return data
    
    def create(self, validated_data):
        """Create payment with auto-assigned client."""
        debt = validated_data['debt']
        validated_data['client'] = debt.client
        return super().create(validated_data)
