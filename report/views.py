from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from client.models import Client
from debt.models import Debt
from payment.models import Payment
from decimal import Decimal


class OutstandingReportView(APIView):
    """Report of all clients with outstanding debts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        clients_with_debts = []
        
        for client in Client.objects.all():
            balance = client.get_balance()
            if balance > 0:
                clients_with_debts.append({
                    'id': client.id,
                    'name': client.name,
                    'email': client.email,
                    'phone': client.phone,
                    'total_debt': float(client.get_total_debt()),
                    'total_paid': float(client.get_total_paid()),
                    'balance': float(balance),
                    'active_debts': client.debts.filter(status='PENDING').count(),
                    'overdue_debts': client.debts.filter(status='OVERDUE').count()
                })
        
        # Sort by balance (highest first)
        clients_with_debts.sort(key=lambda x: x['balance'], reverse=True)
        
        return Response({
            'total_clients': len(clients_with_debts),
            'total_outstanding': sum(c['balance'] for c in clients_with_debts),
            'clients': clients_with_debts
        })


class OverdueReportView(APIView):
    """Report of all overdue debts."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        overdue_debts = Debt.objects.filter(status='OVERDUE').select_related('client')
        
        debts_data = []
        for debt in overdue_debts:
            debts_data.append({
                'id': debt.id,
                'client_name': debt.client.name,
                'client_email': debt.client.email,
                'amount': float(debt.amount),
                'paid': float(debt.get_amount_paid()),
                'remaining': float(debt.get_remaining_balance()),
                'deadline': debt.deadline,
                'days_overdue': abs(debt.days_until_deadline()),
                'description': debt.description
            })
        
        total_overdue = sum(d['remaining'] for d in debts_data)
        
        return Response({
            'total_debts': len(debts_data),
            'total_amount': total_overdue,
            'debts': debts_data
        })


class DashboardStatsView(APIView):
    """Dashboard statistics and overview."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Total clients
        total_clients = Client.objects.count()
        
        # Debt statistics
        total_debts = Debt.objects.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        pending_debts = Debt.objects.filter(status='PENDING').count()
        overdue_debts = Debt.objects.filter(status='OVERDUE').count()
        paid_debts = Debt.objects.filter(status='PAID').count()
        
        # Payment statistics
        total_payments = Payment.objects.aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Calculate outstanding balance
        outstanding_balance = Decimal('0.00')
        for client in Client.objects.all():
            outstanding_balance += client.get_balance()
        
        # Upcoming deadlines (next 7 days)
        today = timezone.now().date()
        upcoming_date = today + timezone.timedelta(days=7)
        upcoming_debts = Debt.objects.filter(
            deadline__gte=today,
            deadline__lte=upcoming_date,
            status='PENDING'
        ).count()
        
        # Recent payments (last 7 days)
        seven_days_ago = today - timezone.timedelta(days=7)
        recent_payments = Payment.objects.filter(date__gte=seven_days_ago).count()
        
        return Response({
            'clients': {
                'total': total_clients,
                'with_debt': Client.objects.filter(debts__isnull=False).distinct().count()
            },
            'debts': {
                'total_count': total_debts['count'] or 0,
                'total_amount': float(total_debts['total'] or Decimal('0.00')),
                'pending': pending_debts,
                'overdue': overdue_debts,
                'paid': paid_debts,
                'upcoming': upcoming_debts
            },
            'payments': {
                'total_count': total_payments['count'] or 0,
                'total_amount': float(total_payments['total'] or Decimal('0.00')),
                'recent_week': recent_payments
            },
            'financial': {
                'outstanding_balance': float(outstanding_balance),
                'collection_rate': self._calculate_collection_rate()
            }
        })
    
    def _calculate_collection_rate(self):
        """Calculate the collection rate percentage."""
        from django.db.models import Sum
        total_debt = Debt.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_paid = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        if total_debt > 0:
            return float((total_paid / total_debt) * 100)
        return 0.0


# Template Views
@login_required
def reports_view(request):
    """Render the reports and analytics page."""
    return render(request, 'reports.html')
