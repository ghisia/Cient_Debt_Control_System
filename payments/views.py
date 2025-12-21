from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment model.
    Provides CRUD operations and custom actions.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments based on query parameters."""
        queryset = Payment.objects.all()
        
        # Filter by client
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by debt
        debt_id = self.request.query_params.get('debt', None)
        if debt_id:
            queryset = queryset.filter(debt_id=debt_id)
        
        return queryset.select_related('client', 'debt')
    
    def get_serializer_class(self):
        """Use create serializer for create action."""
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a payment and return detailed response."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        
        # Return full payment details
        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent payments (last 30 days)."""
        from django.utils import timezone
        thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
        recent_payments = Payment.objects.filter(date__gte=thirty_days_ago)
        serializer = self.get_serializer(recent_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment summary statistics."""
        from django.db.models import Sum, Count
        from decimal import Decimal
        
        total_payments = Payment.objects.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'total_amount': total_payments['total'] or Decimal('0.00'),
            'total_count': total_payments['count'] or 0
        })


# Template Views
@login_required
def payment_list_view(request):
    """Render the payment list page."""
    return render(request, 'payments_list.html')
