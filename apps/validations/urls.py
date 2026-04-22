from django.urls import path
from .views import PendingRequestsView, ValidateRequestView, RefuseRequestView, ValidationHistoryView

urlpatterns = [
    path('pending/', PendingRequestsView.as_view(), name='pending-requests'),
    path('<int:pk>/approve/', ValidateRequestView.as_view(), name='validate-request'),
    path('<int:pk>/refuse/', RefuseRequestView.as_view(), name='refuse-request'),
    path('history/', ValidationHistoryView.as_view(), name='validation-history'),
]