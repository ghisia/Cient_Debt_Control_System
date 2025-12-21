from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Payment(models.Model):
    """
    Payment Model - Tracks payments made by clients towards their debts.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    debt = models.ForeignKey(
        'debt.Debt',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-date', '-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"{self.client.name} - ${self.amount} on {self.date}"
    
    def clean(self):
        """Validate payment amount."""
        if self.amount <= 0:
            raise ValidationError('Payment amount must be greater than zero.')
        
        # Check if payment exceeds remaining debt balance
        if self.debt:
            remaining = self.debt.get_remaining_balance()
            if self.amount > remaining:
                raise ValidationError(
                    f'Payment amount (${self.amount}) exceeds remaining debt balance (${remaining}).'
                )
    
    def save(self, *args, **kwargs):
        """Override save to validate and update debt status."""
        # Ensure client matches debt's client
        if self.debt and self.client != self.debt.client:
            raise ValidationError('Payment client must match debt client.')
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update debt status after payment
        if self.debt:
            self.debt.save()
