from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class ClientManager(BaseUserManager):
    """Custom manager for Client model."""
    
    def create_user(self, email, name, phone, password=None, **extra_fields):
        """Create and save a regular Client user."""
        if not email:
            raise ValueError('The Email field must be set')
        if not name:
            raise ValueError('The Name field must be set')
        if not phone:
            raise ValueError('The Phone field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, phone, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, phone, password, **extra_fields)


class Client(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model for Clients.
    Clients are the customers who have debts to track.
    """
    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Required fields for custom user model
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = ClientManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']
    
    class Meta:
        db_table = 'clients'
        ordering = ['-created_at']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def get_total_debt(self):
        """Calculate total debt amount for this client."""
        return sum(debt.amount for debt in self.debts.all())
    
    def get_total_paid(self):
        """Calculate total amount paid by this client."""
        return sum(payment.amount for payment in self.payments.all())
    
    def get_balance(self):
        """Calculate remaining balance (total debt - total paid)."""
        return self.get_total_debt() - self.get_total_paid()
    
    def has_overdue_debts(self):
        """Check if client has any overdue debts."""
        return self.debts.filter(status='OVERDUE').exists()
