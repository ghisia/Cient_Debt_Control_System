from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationSendSerializer
)


# Template view
@login_required
def notifications_list_view(request):
    """Display list of all notifications"""
    return render(request, 'notifications_list.html')


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification model.
    Provides CRUD operations and custom actions.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications based on query parameters."""
        queryset = Notification.objects.all()
        
        # Filter by client
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        return queryset.select_related('client', 'debt')
    
    def get_serializer_class(self):
        """Use create serializer for create action."""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a specific notification."""
        notification = self.get_object()
        
        if notification.status == 'SENT':
            return Response(
                {'error': 'This notification has already been sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notification.send_email()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def send_pending(self, request):
        """Send all pending notifications that are due."""
        now = timezone.now()
        pending_notifications = Notification.objects.filter(
            status='PENDING',
            scheduled_for__lte=now
        )
        
        sent_count = 0
        failed_count = 0
        
        for notification in pending_notifications:
            notification.send_email()
            if notification.status == 'SENT':
                sent_count += 1
            else:
                failed_count += 1
        
        return Response({
            'message': f'Processed {sent_count + failed_count} notifications',
            'sent': sent_count,
            'failed': failed_count
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending notifications."""
        pending = Notification.objects.filter(status='PENDING')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_reminders(self, request):
        """Create reminders for debts due in 2 days."""
        from debts.models import Debt
        
        created_count = 0
        debts_needing_reminders = Debt.objects.filter(status='PENDING')
        
        for debt in debts_needing_reminders:
            if debt.should_send_reminder():
                # Check if reminder already exists
                existing = Notification.objects.filter(
                    debt=debt,
                    status__in=['PENDING', 'SENT']
                ).exists()
                
                if not existing:
                    vendor_email = request.data.get('vendor_email')
                    Notification.create_debt_reminder(debt, vendor_email)
                    created_count += 1
        
        return Response({
            'message': f'Created {created_count} reminder(s)',
            'count': created_count
        })
