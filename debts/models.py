from django.db import models
from clients.models import Client

class Debt(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='debts'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    deadline = models.DateField()  # ✅ Payment deadline
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.client.name} - {self.amount} ({self.status})"
