from django.urls import path
from .views import OutstandingReportView, OverdueReportView, DashboardStatsView

app_name = 'report'

urlpatterns = [
    path('outstanding/', OutstandingReportView.as_view(), name='outstanding'),
    path('overdue/', OverdueReportView.as_view(), name='overdue'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard'),
]
