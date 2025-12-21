from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail


class Notification(models.Model):
    """
    Notification Model - Tracks email notifications sent to clients and vendors.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    debt = models.ForeignKey(
        'debt.Debt',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    recipient_email = models.EmailField()
    vendor_email = models.EmailField(default=settings.DEFAULT_FROM_EMAIL)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-scheduled_for']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"Notification to {self.client.name} - {self.status}"
    
    def send_email(self):
        """Send the email notification."""
        try:
            send_mail(
                subject=self.subject,
                message=self.message,
                from_email=self.vendor_email,
                recipient_list=[self.recipient_email],
                fail_silently=False,
            )
            self.status = 'SENT'
            self.sent_at = timezone.now()
            self.error_message = None
        except Exception as e:
            self.status = 'FAILED'
            self.error_message = str(e)
        
        self.save()
    
    @classmethod
    def create_debt_reminder(cls, debt, vendor_email=None):
        """
        Create a reminder notification for a debt.
        To be sent 2 days before the deadline.
        """
        if not vendor_email:
            vendor_email = settings.DEFAULT_FROM_EMAIL
        
        scheduled_time = timezone.make_aware(
            timezone.datetime.combine(
                debt.deadline - timezone.timedelta(days=2),
                timezone.datetime.min.time()
            )
        )
        
        message = f"""
Dear {debt.client.name},

This is a reminder that you have an outstanding debt:

Amount: ${debt.amount}
Description: {debt.description}
Deadline: {debt.deadline.strftime('%B %d, %Y')}
Remaining Balance: ${debt.get_remaining_balance()}

Please ensure payment is made before the deadline.

Thank you,
Debt Control System
        """
        
        return cls.objects.create(
            client=debt.client,
            debt=debt,
            recipient_email=debt.client.email,
            vendor_email=vendor_email,
            subject=f'Payment Reminder - Debt Due on {debt.deadline.strftime("%B %d, %Y")}',
            message=message.strip(),
            scheduled_for=scheduled_time,
            status='PENDING'
        )
