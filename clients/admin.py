from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client


@admin.register(Client)
class ClientAdmin(UserAdmin):
    """Admin interface for Client model."""
    
    list_display = ['email', 'name', 'phone', 'created_at', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'name', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login']
