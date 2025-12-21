from django.contrib import admin
from .models import Debt


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    """Admin interface for Debt model."""
    
    list_display = ['client', 'amount', 'deadline', 'status', 'get_remaining_balance', 'created_at']
    list_filter = ['status', 'deadline', 'created_at']
    search_fields = ['client__name', 'client__email', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'deadline'
    
    fieldsets = (
        ('Debt Information', {
            'fields': ('client', 'amount', 'description')
        }),
        ('Dates', {
            'fields': ('date', 'deadline')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_remaining_balance(self, obj):
        """Display remaining balance in admin."""
        return f"${obj.get_remaining_balance():.2f}"
    get_remaining_balance.short_description = 'Remaining Balance'
