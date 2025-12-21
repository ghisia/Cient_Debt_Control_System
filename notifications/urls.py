from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')

app_name = 'notification'

urlpatterns = [
    path('', include(router.urls)),
]
