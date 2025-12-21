from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DebtViewSet

router = DefaultRouter()
router.register(r'', DebtViewSet, basename='debt')

app_name = 'debt'

urlpatterns = [
    path('', include(router.urls)),
]
