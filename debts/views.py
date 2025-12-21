from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Debt
from .serializers import DebtSerializer, DebtDetailSerializer


class DebtViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Debt model.
    Provides CRUD operations and custom actions.
    """
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter debts based on query parameters."""
        queryset = Debt.objects.all()
        
        # Filter by client
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('overdue', None)
        if is_overdue == 'true':
            queryset = queryset.filter(
                deadline__lt=timezone.now().date(),
                status='PENDING'
            )
        
        return queryset.select_related('client')
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return DebtDetailSerializer
        return DebtSerializer
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue debts."""
        overdue_debts = Debt.objects.filter(status='OVERDUE')
        serializer = self.get_serializer(overdue_debts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending debts."""
        pending_debts = Debt.objects.filter(status='PENDING')
        serializer = self.get_serializer(pending_debts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get debts due in the next 7 days."""
        today = timezone.now().date()
        upcoming_date = today + timezone.timedelta(days=7)
        upcoming_debts = Debt.objects.filter(
            deadline__gte=today,
            deadline__lte=upcoming_date,
            status='PENDING'
        )
        serializer = self.get_serializer(upcoming_debts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a debt as paid."""
        debt = self.get_object()
        debt.status = 'PAID'
        debt.save()
        serializer = self.get_serializer(debt)
        return Response(serializer.data)


# Template Views
@login_required
def debt_list_view(request):
    """Render the debt list page."""
    return render(request, 'debts_list.html')


@login_required
def debt_detail_view(request, pk):
    """Render the debt detail page."""
    debt = get_object_or_404(Debt, pk=pk)
    return render(request, 'debt_detail.html', {'debt': debt})
