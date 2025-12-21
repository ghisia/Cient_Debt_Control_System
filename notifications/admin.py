from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    
    list_display = ['client', 'subject', 'status', 'scheduled_for', 'sent_at']
    list_filter = ['status', 'scheduled_for', 'sent_at']
    search_fields = ['client__name', 'client__email', 'subject', 'message']
    ordering = ['-scheduled_for']
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Recipient Information', {
            'fields': ('client', 'debt', 'recipient_email', 'vendor_email')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for', 'sent_at', 'status')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['sent_at', 'created_at']
    
    actions = ['send_notifications']
    
    def send_notifications(self, request, queryset):
        """Admin action to manually send pending notifications."""
        count = 0
        for notification in queryset.filter(status='PENDING'):
            notification.send_email()
            if notification.status == 'SENT':
                count += 1
        
        self.message_user(request, f'{count} notification(s) sent successfully.')
    send_notifications.short_description = 'Send selected notifications'
