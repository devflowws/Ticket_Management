# ticket_backend/apps/employees/urls.py
"""
URLs pour l'application employees
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, QuotaConfigView

router = DefaultRouter()
router.register(r'', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
    path('quota/config/', QuotaConfigView.as_view(), name='quota-config'),
]