from rest_framework import viewsets
from .models import Debt
from .serializers import DebtSerializer

class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
