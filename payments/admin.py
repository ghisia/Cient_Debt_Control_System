from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    
    list_display = ['client', 'debt', 'amount', 'date', 'reference_number', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['client__name', 'client__email', 'reference_number', 'notes']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('client', 'debt', 'amount', 'date')
        }),
        ('Additional Details', {
            'fields': ('reference_number', 'notes')
        }),
    )
    
    readonly_fields = ['created_at']
