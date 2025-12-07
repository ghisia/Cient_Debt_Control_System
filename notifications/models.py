from django.db import models
from clients.models import Client

class Notification(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    vendor_phone = models.CharField(max_length=20)
    message = models.TextField()
    scheduled_for = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.client.name} - {self.status}"

