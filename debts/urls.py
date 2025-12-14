from rest_framework.routers import DefaultRouter
from .views import DebtViewSet

router = DefaultRouter()
router.register(r'debts', DebtViewSet, basename='debt')

urlpatterns = router.urls
