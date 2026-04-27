from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PendingRequestsView, ValidateRequestView, RefuseRequestView, ValidationHistoryView, ValidatorStatsViewSet

router = DefaultRouter()
router.register(r'stats', ValidatorStatsViewSet, basename='validator-stats')

urlpatterns = [
    path('', include(router.urls)),
    path('pending/', PendingRequestsView.as_view(), name='pending-requests'),
    path('<int:pk>/approve/', ValidateRequestView.as_view(), name='validate-request'),
    path('<int:pk>/refuse/', RefuseRequestView.as_view(), name='refuse-request'),
    path('history/', ValidationHistoryView.as_view(), name='validation-history'),
]