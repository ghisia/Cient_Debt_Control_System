from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Debt(models.Model):
    """
    Debt Model - Tracks debts for each client.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'debts'
        ordering = ['-created_at']
        verbose_name = 'Debt'
        verbose_name_plural = 'Debts'
    
    def __str__(self):
        return f"{self.client.name} - ${self.amount} - {self.status}"
    
    def get_amount_paid(self):
        """Calculate total amount paid towards this debt."""
        return sum(payment.amount for payment in self.payments.all())
    
    def get_remaining_balance(self):
        """Calculate remaining balance for this debt."""
        return self.amount - self.get_amount_paid()
    
    def is_overdue(self):
        """Check if debt is overdue."""
        return timezone.now().date() > self.deadline and self.status != 'PAID'
    
    def days_until_deadline(self):
        """Calculate days remaining until deadline."""
        return (self.deadline - timezone.now().date()).days
    
    def should_send_reminder(self):
        """Check if reminder should be sent (2 days before deadline)."""
        days_left = self.days_until_deadline()
        return days_left == 2 and self.status == 'PENDING'
    
    def save(self, *args, **kwargs):
        """Override save to automatically update status."""
        # Auto-update status to OVERDUE if past deadline
        if self.is_overdue() and self.status == 'PENDING':
            self.status = 'OVERDUE'
        
        # Auto-update status to PAID if fully paid (only if debt already exists)
        if self.pk and self.get_remaining_balance() <= 0 and self.status != 'PAID':
            self.status = 'PAID'
        
        super().save(*args, **kwargs)
