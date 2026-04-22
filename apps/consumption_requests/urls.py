from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsumptionRequestViewSet, PendingConsumptionRequestsView

router = DefaultRouter()
router.register(r'', ConsumptionRequestViewSet, basename='consumption-request')

urlpatterns = [
    path('', include(router.urls)),
    path('pending/', PendingConsumptionRequestsView.as_view(), name='pending-requests'),
]