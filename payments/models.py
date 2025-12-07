from django.db import models
from clients.models import Client
from debts.models import Debt

class Payment(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    debt = models.ForeignKey(
        Debt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} - {self.amount}"
