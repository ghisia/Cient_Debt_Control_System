from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    
    total_debt = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    has_overdue_debts = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Client
        fields = [
            'id', 'email', 'name', 'phone', 'address', 'created_at',
            'total_debt', 'total_paid', 'balance', 'has_overdue_debts',
            'is_active', 'password'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_total_debt(self, obj):
        """Get total debt amount."""
        return float(obj.get_total_debt())
    
    def get_total_paid(self, obj):
        """Get total paid amount."""
        return float(obj.get_total_paid())
    
    def get_balance(self, obj):
        """Get remaining balance."""
        return float(obj.get_balance())
    
    def get_has_overdue_debts(self, obj):
        """Check if client has overdue debts."""
        return obj.has_overdue_debts()
    
    def create(self, validated_data):
        """Create a new client with hashed password."""
        password = validated_data.pop('password', None)
        client = Client.objects.create_user(**validated_data, password=password)
        return client
    
    def update(self, instance, validated_data):
        """Update client, handling password separately."""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class ClientBalanceSerializer(serializers.ModelSerializer):
    """Detailed balance information for a client."""
    
    total_debt = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    active_debts_count = serializers.SerializerMethodField()
    overdue_debts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'email', 'phone',
            'total_debt', 'total_paid', 'balance',
            'active_debts_count', 'overdue_debts_count'
        ]
    
    def get_total_debt(self, obj):
        return float(obj.get_total_debt())
    
    def get_total_paid(self, obj):
        return float(obj.get_total_paid())
    
    def get_balance(self, obj):
        return float(obj.get_balance())
    
    def get_active_debts_count(self, obj):
        return obj.debts.filter(status='PENDING').count()
    
    def get_overdue_debts_count(self, obj):
        return obj.debts.filter(status='OVERDUE').count()
